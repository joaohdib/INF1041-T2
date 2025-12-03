from __future__ import annotations

from typing import Any, Dict, Optional

from domain.meta import Meta
from domain.reserva import Reserva

from use_cases.repository_interfaces import IMetaRepository, IReservaRepository


class _ReservaUseCaseBase:
    def __init__(self, reserva_repo: IReservaRepository, meta_repo: IMetaRepository):
        self.reserva_repo = reserva_repo
        self.meta_repo = meta_repo

    def _converter_valor(self, valor: Any) -> float:
        try:
            valor_float = float(valor)
        except (TypeError, ValueError):
            raise ValueError(
                "Informe um valor numérico válido para a reserva.")
        if valor_float <= 0:
            raise ValueError("O valor da reserva deve ser positivo.")
        return valor_float

    def _recalcular_meta(self, meta_id: str):
        """Recalcula e retorna a entidade Meta atualizada."""
        meta = self.meta_repo.get_by_id(meta_id)
        if not meta:
            raise ValueError("Meta vinculada não encontrada.")

        total_reservado = self.reserva_repo.get_total_by_meta(meta_id)
        meta.atualizar_valor_atual(total_reservado)
        self.meta_repo.update(meta)
        return meta


class CriarReserva(_ReservaUseCaseBase):
    def execute(
        self,
        *,
        id_usuario: str,
        id_meta: str,
        valor: Any,
        id_transacao: Optional[str] = None,
        observacao: Optional[str] = None,
    ) -> Dict[str, Any]:
        meta = self.meta_repo.get_by_id(id_meta)
        if not meta:
            raise ValueError("Meta não encontrada para associar a reserva.")
        if meta.esta_concluida():
            raise ValueError(
                "Meta já concluída não pode receber novas reservas.")

        valor_float = self._converter_valor(valor)

        reserva = Reserva(
            id_usuario=id_usuario,
            id_meta=id_meta,
            valor=valor_float,
            id_transacao=id_transacao,
            observacao=observacao,
        )

        self.reserva_repo.add(reserva)
        meta_atualizada = self._recalcular_meta(id_meta)

        return {
            "reserva": reserva,
            "meta": meta_atualizada,
        }


class AtualizarReserva(_ReservaUseCaseBase):
    def execute(
        self,
        *,
        id_usuario: str,
        id_reserva: str,
        novo_valor: Any,
        observacao: Optional[str] = None,
    ) -> Dict[str, Any]:
        reserva = self.reserva_repo.get_by_id(id_reserva)
        if not reserva:
            raise ValueError("Reserva não encontrada.")
        if reserva.id_usuario != id_usuario:
            raise PermissionError(
                "Usuário não autorizado a alterar esta reserva.")

        valor_float = self._converter_valor(novo_valor)
        reserva.atualizar_valor(valor_float)
        reserva.observacao = (
            observacao if observacao is not None else reserva.observacao
        )

        self.reserva_repo.update(reserva)
        meta_atualizada = self._recalcular_meta(reserva.id_meta)

        return {
            "reserva": reserva,
            "meta": meta_atualizada,
        }


class ExcluirReserva(_ReservaUseCaseBase):
    def execute(self, *, id_usuario: str, id_reserva: str) -> Dict[str, Any]:
        reserva = self.reserva_repo.get_by_id(id_reserva)
        if not reserva:
            raise ValueError("Reserva não encontrada.")
        if reserva.id_usuario != id_usuario:
            raise PermissionError(
                "Usuário não autorizado a excluir esta reserva.")

        id_meta = reserva.id_meta
        self.reserva_repo.delete(id_reserva)
        meta_atualizada = self._recalcular_meta(id_meta)

        return {
            "meta": meta_atualizada,
        }


class ListarMetasDisponiveisParaReserva:
    def __init__(self, meta_repo: IMetaRepository):
        self.meta_repo = meta_repo

    def execute(self, id_usuario: str) -> List[Meta]:
        metas = self.meta_repo.get_by_usuario(id_usuario)
        return [meta for meta in metas if not meta.esta_concluida()]
