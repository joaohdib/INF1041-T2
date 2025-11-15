from __future__ import annotations
from dataclasses import asdict
from datetime import datetime, date
import math
from typing import Dict, Any

from domain.meta import Meta
from use_cases.repository_interfaces import IMetaRepository, IMetaUsoRepository


class MetaCalculator:
    @staticmethod
    def _days_until(deadline: datetime) -> int:
        today = date.today()
        end = deadline.date()
        return (end - today).days

    @staticmethod
    def periodic_suggestions(valor_total: float, deadline: datetime) -> Dict[str, float]:
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

    def execute(self, *, id_usuario: str, nome: str, valor_alvo: Any, data_limite: Any,
                id_perfil: str | None = None) -> Dict[str, Any]:
        if not nome or str(nome).strip() == "":
            raise ValueError("Nome é obrigatório.")

        try:
            valor = float(valor_alvo)
        except (TypeError, ValueError):
            raise ValueError("Informe um valor numérico válido para 'Valor'.")
        if valor <= 0:
            raise ValueError("O valor deve ser maior que zero.")

        if not data_limite:
            raise ValueError("Data Final é obrigatória para o planejamento da meta.")

        if isinstance(data_limite, str):
            try:
                deadline = datetime.fromisoformat(data_limite)
            except ValueError:
                try:
                    deadline = datetime.strptime(data_limite, '%Y-%m-%d')
                except ValueError:
                    raise ValueError("Data Final deve estar em formato ISO (YYYY-MM-DD) ou (YYYY-MM-DDTHH:MM:SS).")
        elif isinstance(data_limite, datetime):
            deadline = data_limite
        else:
            raise ValueError("Formato de Data Final inválido.")

        if deadline.date() <= datetime.now().date():
            raise ValueError("A data limite deve ser futura.")

        sugestoes = MetaCalculator.periodic_suggestions(valor, deadline)

        meta = Meta(
            id_usuario=id_usuario,
            nome=nome,
            valor_alvo=valor,
            data_limite=deadline,
            id_perfil=id_perfil
        )

        self.meta_repo.add(meta)

        return {
            "id": meta.id,
            "nome": meta.nome,
            "valor_alvo": meta.valor_alvo,
            "data_limite": meta.data_limite.isoformat(),
            "sugestoes": sugestoes
        }

class ConcluirMeta:
    def __init__(self, meta_repo: IMetaRepository):
        self.meta_repo = meta_repo

    def execute(self, *, id_meta: str, id_usuario: str) -> Dict[str, Any]:
        meta = self.meta_repo.get_by_id(id_meta)
        if not meta:
            raise ValueError("Meta não encontrada.")
        if meta.id_usuario != id_usuario:
            raise ValueError("Operação não permitida.")
        if meta.esta_concluida():
            raise ValueError("Meta já está concluída.")

        print(f"USE CASE: Concluindo meta {id_meta}")
        meta.concluir_manual()
        print(f"USE CASE: Meta concluída - concluida_em: {meta.concluida_em}")
        
        # Força a atualização chamando explicitamente o update
        self.meta_repo.update(meta)
        print(f"USE CASE: Meta atualizada no repositório")

        # Recupera a meta novamente para verificar se foi atualizada
        meta_verificada = self.meta_repo.get_by_id(id_meta)
        print(f"USE CASE: Meta verificada - concluida: {meta_verificada.esta_concluida()}, concluida_em: {meta_verificada.concluida_em}")

        return {
            "id": meta.id,
            "concluida_em": meta.concluida_em.isoformat(),
            "mensagem": "Meta concluída com sucesso!"
        }

class RegistrarUsoMeta:
    def __init__(self, meta_repo: IMetaRepository, meta_uso_repo: IMetaUsoRepository):
        self.meta_repo = meta_repo
        self.meta_uso_repo = meta_uso_repo

    def execute(self, *, id_meta: str, id_transacao: str, id_usuario: str) -> Dict[str, Any]:
        meta = self.meta_repo.get_by_id(id_meta)
        if not meta:
            raise ValueError("Meta não encontrada.")
        if meta.id_usuario != id_usuario:
            raise ValueError("Operação não permitida.")
        if not meta.esta_concluida():
            raise ValueError("A meta deve estar concluída para registrar uso.")
        if meta.esta_finalizada():
            raise ValueError("Meta já finalizada.")

        transacao = self.meta_uso_repo.get_transacao(id_transacao)
        if not transacao:
            raise ValueError("Transação não encontrada.")
        if transacao.id_usuario != id_usuario:
            raise ValueError("Transação não pertence ao usuário.")

        meta_uso = self.meta_uso_repo.add_uso(id_meta, id_transacao, transacao.valor)

        return {
            "id_meta": id_meta,
            "id_transacao": id_transacao,
            "valor_utilizado": transacao.valor
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

        print(f"USE CASE: Finalizando meta {id_meta}")
        meta.finalizar()
        print(f"USE CASE: Meta finalizada - finalizada_em: {meta.finalizada_em}")
        
        self.meta_repo.update(meta)
        print(f"USE CASE: Meta finalizada no repositório")

        return {
            "id_meta": id_meta,
            "valor_total_meta": meta.valor_atual,
            "valor_utilizado": total_utilizado,
            "saldo_restante": saldo_restante,
            "finalizada_em": meta.finalizada_em.isoformat()
        }