import csv
import io
import os
import re
from datetime import datetime
from typing import Dict, List, Any

from domain.transacao import Transacao, StatusTransacao, TipoTransacao
from domain.mapeamento_csv import MapeamentoCSV
from use_cases.repository_interfaces import (
    ITransacaoRepository,
    IMapeamentoCSVRepository,
)


class ImportarExtratoBancario:
    """Caso de uso responsável por importar arquivos CSV/OFX."""

    SUPPORTED_EXTENSIONS = {".csv", ".ofx"}
    CSV_DEFAULT_MAP = {
        "data": {"data", "date", "dt", "transaction date"},
        "valor": {"valor", "value", "amount", "vl"},
        "descricao": {"descricao", "description", "memo", "history"},
    }
    DATE_FORMATS = ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%m/%d/%Y"]

    def __init__(
        self,
        transacao_repo: ITransacaoRepository,
        mapeamento_repo: IMapeamentoCSVRepository | None = None,
    ):
        self.transacao_repo = transacao_repo
        self.mapeamento_repo = mapeamento_repo

    def execute(
        self,
        id_usuario: str,
        file_bytes: bytes,
        file_name: str,
        column_mapping: Dict[str, str] | None = None,
        mapping_id: str | None = None,
        sem_cabecalho: bool = False,
    ) -> Dict[str, Any]:
        if not file_name:
            raise ValueError("Arquivo não enviado.")

        extension = os.path.splitext(file_name)[1].lower()
        if extension not in self.SUPPORTED_EXTENSIONS:
            raise ValueError("Formato de arquivo inválido. Use CSV ou OFX.")

        if not file_bytes:
            raise ValueError("Arquivo vazio. Nenhuma transação encontrada.")

        resolved_mapping, resolved_sem_cabecalho = self._resolve_mapping_param(
            id_usuario=id_usuario,
            mapping_id=mapping_id,
            column_mapping=column_mapping,
            extension=extension,
            sem_cabecalho_flag=sem_cabecalho,
        )

        if extension == ".csv":
            transacoes = self._parse_csv(
                file_bytes,
                resolved_mapping,
                sem_cabecalho=resolved_sem_cabecalho,
            )
        else:
            transacoes = self._parse_ofx(file_bytes)

        if not transacoes:
            raise ValueError("Nenhuma transação válida encontrada no arquivo enviado.")

        for dados in transacoes:
            transacao = Transacao(
                id_usuario=id_usuario,
                valor=dados["valor"],
                tipo=dados["tipo"],
                data=dados["data"],
                descricao=dados.get("descricao"),
                status=StatusTransacao.PENDENTE,
            )
            self.transacao_repo.add(transacao)

        return {"total_importadas": len(transacoes)}

    # --- CSV helpers ---

    def _parse_csv(
        self,
        file_bytes: bytes,
        column_mapping: Dict[str, str] | None,
        sem_cabecalho: bool = False,
    ) -> List[Dict[str, Any]]:
        texto = file_bytes.decode("utf-8-sig")

        try:
            sample = texto[:1024]
            dialect = csv.Sniffer().sniff(sample, delimiters=",;\t")
        except csv.Error:
            dialect = csv.excel

        linhas = []
        reader = csv.reader(io.StringIO(texto), dialect=dialect)
        for row in reader:
            normalizada = [col.strip() for col in row]
            if not any(normalizada):
                continue
            linhas.append(normalizada)

        if not linhas:
            raise ValueError("Arquivo CSV sem dados.")

        if sem_cabecalho:
            fieldnames = [f"__col_{i}" for i in range(len(linhas[0]))]
            data_rows = linhas
        else:
            raw_headers = linhas[0]
            fieldnames = [
                (header.strip() or f"col_{idx}") for idx, header in enumerate(raw_headers)
            ]
            data_rows = linhas[1:]

        if not data_rows:
            raise ValueError("Nenhuma transação válida encontrada no arquivo enviado.")

        mapping = self._resolve_mapping(fieldnames, column_mapping, sem_cabecalho)

        transacoes = []
        for row in data_rows:
            row_dict = {
                fieldnames[idx]: row[idx].strip() if idx < len(row) else ""
                for idx in range(len(fieldnames))
            }

            try:
                data_str = (row_dict.get(mapping["data"]) or "").strip()
                valor_raw = (row_dict.get(mapping["valor"]) or "").strip()
                descricao = (row_dict.get(mapping["descricao"]) or "").strip()

                data = self._parse_date(data_str)
                valor, tipo = self._parse_valor(valor_raw)

                transacoes.append(
                    {
                        "data": data,
                        "valor": valor,
                        "tipo": tipo,
                        "descricao": descricao or None,
                    }
                )
            except ValueError as exc:
                raise ValueError(
                    f"Arquivo CSV inválido: {exc}. Linha: {row_dict}"
                ) from exc

        return transacoes

    def _resolve_mapping(
        self,
        header: List[str],
        column_mapping: Dict[str, str] | None,
        sem_cabecalho: bool = False,
    ) -> Dict[str, str]:
        normalized_header = [col.strip() for col in header]

        if column_mapping:
            mapping = {}
            valores_utilizados = set()
            for campo, nome_coluna in column_mapping.items():
                if nome_coluna not in normalized_header:
                    raise ValueError(
                        f"Coluna '{nome_coluna}' não encontrada no CSV para o campo '{campo}'."
                    )
                if nome_coluna in valores_utilizados:
                    raise ValueError(
                        "Cada campo (Data, Valor, Descrição) deve usar colunas diferentes no CSV."
                    )
                valores_utilizados.add(nome_coluna)
                mapping[campo] = nome_coluna
            return mapping

        if sem_cabecalho:
            raise ValueError(
                "Mapeie manualmente as colunas (Data, Valor e Descrição) para arquivos sem cabeçalho."
            )

        mapping = {}
        lower_header = {col.lower(): col for col in normalized_header}
        for campo, candidatos in self.CSV_DEFAULT_MAP.items():
            encontrado = None
            for candidato in candidatos:
                if candidato in lower_header:
                    encontrado = lower_header[candidato]
                    break
            if not encontrado:
                raise ValueError(
                    "CSV sem as colunas esperadas (Data, Valor, Descrição)."
                )
            mapping[campo] = encontrado
        return mapping

    # --- OFX helpers ---

    def _parse_ofx(self, file_bytes: bytes) -> List[Dict[str, Any]]:
        texto = file_bytes.decode("latin-1")
        transacoes = []
        atual: Dict[str, str] | None = None

        for line in texto.splitlines():
            line = line.strip()
            if not line:
                continue

            upper = line.upper()
            if upper.startswith("<STMTTRN>"):
                atual = {}
                continue

            if upper.startswith("</STMTTRN>"):
                if atual:
                    transacoes.append(self._build_ofx_transacao(atual))
                atual = None
                continue

            if atual is None:
                continue

            match = re.match(r"<([^>]+)>(.*)", line)
            if not match:
                continue

            tag, value = match.groups()
            atual[tag.upper()] = value.strip()

        return [t for t in transacoes if t]

    def _build_ofx_transacao(self, dados: Dict[str, str]) -> Dict[str, Any] | None:
        try:
            data = self._parse_ofx_date(dados.get("DTPOSTED", ""))
            valor, tipo = self._parse_valor(dados.get("TRNAMT", ""))
            descricao = dados.get("MEMO") or dados.get("NAME")
        except ValueError:
            return None

        return {
            "data": data,
            "valor": valor,
            "tipo": tipo,
            "descricao": descricao,
        }

    # --- utilitários ---

    def _parse_date(self, raw: str) -> datetime:
        if not raw:
            raise ValueError("Coluna de data vazia.")

        for fmt in self.DATE_FORMATS:
            try:
                return datetime.strptime(raw, fmt)
            except ValueError:
                continue

        raise ValueError(f"Formato de data inválido: {raw}")

    def _parse_ofx_date(self, raw: str) -> datetime:
        if not raw:
            raise ValueError("Registro OFX sem data.")
        numeros = re.findall(r"\d+", raw)
        if not numeros:
            raise ValueError(f"Data OFX inválida: {raw}")
        data_str = numeros[0]
        return datetime.strptime(data_str[:8], "%Y%m%d")

    def _parse_valor(self, raw: str) -> tuple[float, TipoTransacao]:
        if raw is None:
            raise ValueError("Valor ausente.")

        if isinstance(raw, (int, float)):
            valor_float = float(raw)
        else:
            texto = raw.strip().replace("R$", "")
            texto = texto.replace(" ", "")
            if "," in texto and "." in texto:
                texto = texto.replace(".", "").replace(",", ".")
            elif "," in texto:
                texto = texto.replace(",", ".")
            if not texto:
                raise ValueError("Valor vazio.")
            valor_float = float(texto)

        tipo = TipoTransacao.RECEITA if valor_float >= 0 else TipoTransacao.DESPESA
        return abs(valor_float), tipo

    # --- mapping helpers ---

    def _resolve_mapping_param(
        self,
        id_usuario: str,
        mapping_id: str | None,
        column_mapping: Dict[str, str] | None,
        extension: str,
        sem_cabecalho_flag: bool,
    ) -> tuple[Dict[str, str] | None, bool]:
        if extension != ".csv":
            return None, False

        sem_cabecalho = sem_cabecalho_flag

        if mapping_id:
            if not self.mapeamento_repo:
                raise ValueError("Repositório de mapeamentos indisponível.")
            mapeamento = self.mapeamento_repo.get_by_id(mapping_id)
            if not mapeamento or mapeamento.id_usuario != id_usuario:
                raise ValueError("Mapeamento não encontrado para este usuário.")
            sem_cabecalho = all(
                coluna.startswith("__col_")
                for coluna in [
                    mapeamento.coluna_data,
                    mapeamento.coluna_valor,
                    mapeamento.coluna_descricao,
                ]
            )
            return (
                {
                    "data": mapeamento.coluna_data,
                    "valor": mapeamento.coluna_valor,
                    "descricao": mapeamento.coluna_descricao,
                },
                sem_cabecalho,
            )

        return column_mapping, sem_cabecalho


class SalvarMapeamentoCSV:
    def __init__(self, repo: IMapeamentoCSVRepository):
        self.repo = repo

    def execute(
        self,
        id_usuario: str,
        nome: str,
        coluna_data: str,
        coluna_valor: str,
        coluna_descricao: str,
    ) -> MapeamentoCSV:
        nome = (nome or "").strip()
        if not nome:
            raise ValueError("Informe um nome para o mapeamento.")

        colunas = {
            "data": (coluna_data or "").strip(),
            "valor": (coluna_valor or "").strip(),
            "descricao": (coluna_descricao or "").strip(),
        }

        if not all(colunas.values()):
            raise ValueError("Mapeamento inválido: Data, Valor e Descrição são obrigatórios.")

        if len(set(colunas.values())) < 3:
            raise ValueError("Cada coluna essencial deve ser única.")

        if self.repo.exists_nome(id_usuario, nome):
            raise ValueError("Já existe um mapeamento com este nome.")

        entidade = MapeamentoCSV(
            id_usuario=id_usuario,
            nome=nome,
            coluna_data=colunas["data"],
            coluna_valor=colunas["valor"],
            coluna_descricao=colunas["descricao"],
        )

        return self.repo.add(entidade)


class ListarMapeamentosCSV:
    def __init__(self, repo: IMapeamentoCSVRepository):
        self.repo = repo

    def execute(self, id_usuario: str) -> List[MapeamentoCSV]:
        return self.repo.get_by_usuario(id_usuario)
