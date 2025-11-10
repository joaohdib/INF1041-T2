from __future__ import annotations
from dataclasses import asdict
from datetime import datetime, date
import math
from typing import Dict, Any

from domain.meta import Meta
from use_cases.repository_interfaces import IMetaRepository


class MetaCalculator:
    """Módulo isolado para cálculos de metas (DoD)."""

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
            raise ValueError("Data Final é obrigatória para o planejamento da meta.")

        if isinstance(data_limite, str):
            try:
                deadline = datetime.fromisoformat(data_limite)
            except ValueError:
                raise ValueError("Data Final deve estar em formato ISO (YYYY-MM-DD).")
        elif isinstance(data_limite, datetime):
            deadline = data_limite
        else:
            raise ValueError("Formato de Data Final inválido.")

        # Validação de futuro é reforçada também no domínio
        if deadline <= datetime.now():
            raise ValueError("A data limite deve ser futura.")

        # 2. Calcula sugestões
        sugestoes = MetaCalculator.periodic_suggestions(valor, deadline)

        # 3. Cria entidade e persiste
        meta = Meta(
            id_usuario=id_usuario,
            nome=nome,
            valor_alvo=valor,
            data_limite=deadline,
            id_perfil=id_perfil
        )

        self.meta_repo.add(meta)

        # 4. Retorno resumido
        return {
            "id": meta.id,
            "nome": meta.nome,
            "valor_alvo": meta.valor_alvo,
            "data_limite": meta.data_limite.isoformat(),
            "sugestoes": sugestoes
        }
