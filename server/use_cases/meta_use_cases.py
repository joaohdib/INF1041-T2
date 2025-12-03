from __future__ import annotations

import math
from datetime import datetime, date
from typing import Any, Dict

from domain.meta import Meta, StatusMeta
from use_cases.repository_interfaces import (
    IMetaRepository,
    IMetaUsoRepository,
    ITransacaoRepository,
)


class MetaCalculator:
    """Módulo isolado para cálculos de metas (DoD)."""

    @staticmethod
    def _days_until(deadline: datetime) -> int:
        today = date.today()
        end = deadline.date()
        return (end - today).days

    @staticmethod
    def periodic_suggestions(
        valor_total: float, deadline: datetime
    ) -> Dict[str, float]:
        days = MetaCalculator._days_until(deadline)
        if days <= 0:
            raise ValueError("A data limite deve ser futura.")

        weeks = max(1, math.ceil(days / 7))
        months = max(1, math.ceil(days / 30))

        weekly = round(valor_total / weeks, 2)
        monthly = round(valor_total / months, 2)
        return {"semanal": weekly, "mensal": monthly}


class CriarMeta:
    def __init__(self, meta_repo: IMetaRepository):
        self.meta_repo = meta_repo

    def execute(
        self,
        *,
        id_usuario: str,
        nome: str,
        valor_alvo: Any,
        data_limite: Any,
        id_perfil: str | None = None,
    ) -> Dict[str, Any]:
        # 1. Validações e normalização
        if not nome or str(nome).strip() == "":
            raise ValueError("Nome é obrigatório.")

        try:
            valor = float(valor_alvo)
        except (TypeError, ValueError):
            raise ValueError("Informe um valor numérico válido para 'Valor'.")
        if valor <= 0:
            raise ValueError("O valor deve ser maior que zero.")

        if not data_limite:
            raise ValueError(
                "Data Final é obrigatória para o planejamento da meta.")

        if isinstance(data_limite, str):
            try:
                deadline = datetime.fromisoformat(data_limite)
            except ValueError:
                try:
                    deadline = datetime.strptime(data_limite, "%Y-%m-%d")
                except ValueError:
                    raise ValueError(
                        "Data Final deve estar em formato ISO (YYYY-MM-DD) "
                        "ou (YYYY-MM-DDTHH:MM:SS)."
                    )
        elif isinstance(data_limite, datetime):
            deadline = data_limite
        else:
            raise ValueError("Formato de Data Final inválido.")

        # Validação de futuro (apenas data, ignorando horário)
        if deadline.date() <= datetime.now().date():
            raise ValueError("A data limite deve ser futura.")

        # 2. Calcula sugestões
        sugestoes = MetaCalculator.periodic_suggestions(valor, deadline)

        # 3. Cria entidade e persiste
        meta = Meta(
            id_usuario=id_usuario,
            nome=nome,
            valor_alvo=valor,
            data_limite=deadline,
            id_perfil=id_perfil,
        )

        self.meta_repo.add(meta)

        # 4. Retorno sem formatação de apresentação
        return {"meta": meta, "sugestoes": sugestoes}


class EditarMeta:
    def __init__(self, meta_repo: IMetaRepository):
        self.meta_repo = meta_repo

    def execute(
        self,
        *,
        id_meta: str,
        id_usuario: str,
        nome: str,
        valor_alvo: Any,
        data_limite: Any,
    ) -> Meta:
        meta = self.meta_repo.get_by_id(id_meta)
        if not meta:
            raise ValueError("Meta não encontrada.")
        if meta.id_usuario != id_usuario:
            raise ValueError("Operação não permitida.")
        if meta.status == StatusMeta.CONCLUIDA:
            raise ValueError("Não é possível editar uma meta concluída.")

        # Validações dos novos valores
        if not nome or str(nome).strip() == "":
            raise ValueError("Nome é obrigatório.")

        try:
            valor = float(valor_alvo)
        except (TypeError, ValueError):
            raise ValueError("Informe um valor numérico válido para 'Valor'.")
        if valor <= 0:
            raise ValueError("O valor deve ser maior que zero.")

        if not data_limite:
            raise ValueError("Data Final é obrigatória.")

        if isinstance(data_limite, str):
            try:
                deadline = datetime.fromisoformat(data_limite)
            except ValueError:
                try:
                    deadline = datetime.strptime(data_limite, "%Y-%m-%d")
                except ValueError:
                    raise ValueError("Data Final deve estar em formato ISO.")
        elif isinstance(data_limite, datetime):
            deadline = data_limite
        else:
            raise ValueError("Formato de Data Final inválido.")

        if deadline.date() <= datetime.now().date():
            raise ValueError("A data limite deve ser futura.")

        # Aplica as alterações
        meta.editar(nome, valor, deadline)
        self.meta_repo.update(meta)

        return meta


class PausarMeta:
    def __init__(self, meta_repo: IMetaRepository):
        self.meta_repo = meta_repo

    def execute(self, *, id_meta: str, id_usuario: str) -> Meta:
        meta = self.meta_repo.get_by_id(id_meta)
        if not meta:
            raise ValueError("Meta não encontrada.")
        if meta.id_usuario != id_usuario:
            raise ValueError("Operação não permitida.")
        if meta.status == StatusMeta.CONCLUIDA:
            raise ValueError("Não é possível pausar uma meta concluída.")

        meta.pausar()
        self.meta_repo.update(meta)

        return meta


class RetomarMeta:
    def __init__(self, meta_repo: IMetaRepository):
        self.meta_repo = meta_repo

    def execute(self, *, id_meta: str, id_usuario: str) -> Meta:
        meta = self.meta_repo.get_by_id(id_meta)
        if not meta:
            raise ValueError("Meta não encontrada.")
        if meta.id_usuario != id_usuario:
            raise ValueError("Operação não permitida.")
        if meta.status != StatusMeta.PAUSADA:
            raise ValueError("Só é possível retomar metas pausadas.")

        meta.retomar()
        self.meta_repo.update(meta)

        return meta


class CancelarMeta:
    def __init__(self, meta_repo: IMetaRepository):
        self.meta_repo = meta_repo

    def execute(
        self,
        *,
        id_meta: str,
        id_usuario: str,
        acao_fundos: str,
        id_meta_destino: str | None = None,
    ) -> Dict[str, Any]:
        meta = self.meta_repo.get_by_id(id_meta)
        if not meta:
            raise ValueError("Meta não encontrada.")
        if meta.id_usuario != id_usuario:
            raise ValueError("Operação não permitida.")
        if meta.status == StatusMeta.CONCLUIDA:
            raise ValueError("Não é possível cancelar uma meta concluída.")

        if acao_fundos not in ["manter", "liberar", "realocar"]:
            raise ValueError("Ação de fundos inválida.")

        if acao_fundos == "realocar" and not id_meta_destino:
            raise ValueError(
                "ID da meta destino é obrigatório para realocação.")

        # Realocar fundos se necessário
        if acao_fundos == "realocar":
            meta_destino = self.meta_repo.get_by_id(id_meta_destino)
            if not meta_destino:
                raise ValueError("Meta destino não encontrada.")
            if meta_destino.id_usuario != id_usuario:
                raise ValueError("Meta destino não pertence ao usuário.")
            if meta_destino.status != StatusMeta.ATIVA:
                raise ValueError("Meta destino deve estar ativa.")

            # Transfere o valor
            meta_destino.registrar_aporte(meta.valor_atual)
            self.meta_repo.update(meta_destino)

        # Liberar ou manter fundos (manter = valor_atual permanece, mas meta cancelada)
        if acao_fundos == "liberar":
            meta.valor_atual = 0.0

        meta.cancelar()
        self.meta_repo.update(meta)

        return {
            "meta": meta,
            "acao_fundos": acao_fundos,
            "id_meta_destino": id_meta_destino,
        }


class ConcluirMeta:
    def __init__(self, meta_repo: IMetaRepository):
        self.meta_repo = meta_repo

    def execute(self, *, id_meta: str, id_usuario: str) -> Meta:
        meta = self.meta_repo.get_by_id(id_meta)
        if not meta:
            raise ValueError("Meta não encontrada.")
        if meta.id_usuario != id_usuario:
            raise ValueError("Operação não permitida.")
        if meta.esta_concluida():
            raise ValueError("Meta já está concluída.")

        meta.concluir_manual()
        self.meta_repo.update(meta)

        return meta


class RegistrarUsoMeta:
    def __init__(
        self,
        meta_repo: IMetaRepository,
        meta_uso_repo: IMetaUsoRepository,
        transacao_repo: ITransacaoRepository,
    ):
        self.meta_repo = meta_repo
        self.meta_uso_repo = meta_uso_repo
        self.transacao_repo = transacao_repo

    def execute(
        self, *, id_meta: str, id_transacao: str, id_usuario: str
    ) -> Dict[str, Any]:
        meta = self.meta_repo.get_by_id(id_meta)
        if not meta:
            raise ValueError("Meta não encontrada.")
        if meta.id_usuario != id_usuario:
            raise ValueError("Operação não permitida.")
        if not meta.esta_concluida():
            raise ValueError("A meta deve estar concluída para registrar uso.")
        if meta.esta_finalizada():
            raise ValueError("Meta já finalizada.")

        transacao = self.transacao_repo.get_by_id(id_transacao)
        if not transacao:
            raise ValueError("Transação não encontrada.")
        if transacao.id_usuario != id_usuario:
            raise ValueError("Transação não pertence ao usuário.")

        meta_uso = self.meta_uso_repo.add_uso(
            id_meta, id_transacao, transacao.valor)

        return {
            "meta": meta,
            "valor_utilizado": transacao.valor,
        }


class LiberarSaldoMeta:
    def __init__(self, meta_repo: IMetaRepository, meta_uso_repo: IMetaUsoRepository):
        self.meta_repo = meta_repo
        self.meta_uso_repo = meta_uso_repo

    def execute(self, *, id_meta: str, id_usuario: str) -> Dict[str, Any]:
        meta = self.meta_repo.get_by_id(id_meta)
        if not meta:
            raise ValueError("Meta não encontrada.")
        if meta.id_usuario != id_usuario:
            raise ValueError("Operação não permitida.")
        if not meta.esta_concluida():
            raise ValueError("A meta deve estar concluída para liberar saldo.")
        if meta.esta_finalizada():
            raise ValueError("Meta já finalizada.")

        total_utilizado = self.meta_uso_repo.sum_uso_por_meta(id_meta)
        saldo_restante = meta.valor_atual - total_utilizado

        meta.finalizar()
        self.meta_repo.update(meta)

        return {
            "meta": meta,
            "valor_total_meta": meta.valor_atual,
            "valor_utilizado": total_utilizado,
            "saldo_restante": saldo_restante,
        }
