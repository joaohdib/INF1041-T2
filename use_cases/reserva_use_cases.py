from __future__ import annotations
from typing import Dict, Any, Optional

from domain.reserva import Reserva
from use_cases.repository_interfaces import IReservaRepository, IMetaRepository


class _ReservaUseCaseBase:
    def __init__(self, reserva_repo: IReservaRepository, meta_repo: IMetaRepository):
        self.reserva_repo = reserva_repo
        self.meta_repo = meta_repo

    def _converter_valor(self, valor: Any) -> float:
        try:
            valor_float = float(valor)
        except (TypeError, ValueError):
            raise ValueError("Informe um valor numérico válido para a reserva.")
        if valor_float <= 0:
            raise ValueError("O valor da reserva deve ser positivo.")
        return valor_float

    def _recalcular_meta(self, meta_id: str) -> Dict[str, Any]:
        meta = self.meta_repo.get_by_id(meta_id)
        if not meta:
            raise ValueError("Meta vinculada não encontrada.")

        total_reservado = self.reserva_repo.get_total_by_meta(meta_id)
        meta.atualizar_valor_atual(total_reservado)
        self.meta_repo.update(meta)

        payload = {
            "id": meta.id,
            "nome": meta.nome,
            "valor_alvo": meta.valor_alvo,
            "valor_atual": meta.valor_atual,
            "progresso_percentual": meta.progresso_percentual(),
            "esta_concluida": meta.esta_concluida(),
            "concluida_em": meta.concluida_em.isoformat() if meta.concluida_em else None,
        }
        if payload["esta_concluida"]:
            payload["mensagem"] = "Meta concluída! Parabéns pelo objetivo atingido."
        return payload

    @staticmethod
    def _serializar_reserva(reserva: Reserva) -> Dict[str, Any]:
        return {
            "id": reserva.id,
            "id_usuario": reserva.id_usuario,
            "id_meta": reserva.id_meta,
            "valor": reserva.valor,
            "id_transacao": reserva.id_transacao,
            "observacao": reserva.observacao,
            "criado_em": reserva.criado_em.isoformat() if reserva.criado_em else None,
            "atualizado_em": reserva.atualizado_em.isoformat() if reserva.atualizado_em else None,
        }


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
            raise ValueError("Meta já concluída não pode receber novas reservas.")

        valor_float = self._converter_valor(valor)

        reserva = Reserva(
            id_usuario=id_usuario,
            id_meta=id_meta,
            valor=valor_float,
            id_transacao=id_transacao,
            observacao=observacao,
        )

        self.reserva_repo.add(reserva)
        meta_payload = self._recalcular_meta(id_meta)

        resposta = {
            "reserva": self._serializar_reserva(reserva),
            "meta": meta_payload,
        }
        if meta_payload.get("mensagem"):
            resposta["mensagem"] = meta_payload["mensagem"]
        return resposta


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
            raise PermissionError("Usuário não autorizado a alterar esta reserva.")

        valor_float = self._converter_valor(novo_valor)
        reserva.atualizar_valor(valor_float)
        reserva.observacao = observacao if observacao is not None else reserva.observacao

        self.reserva_repo.update(reserva)
        meta_payload = self._recalcular_meta(reserva.id_meta)

        return {
            "reserva": self._serializar_reserva(reserva),
            "meta": meta_payload,
        }


class ExcluirReserva(_ReservaUseCaseBase):
    def execute(self, *, id_usuario: str, id_reserva: str) -> Dict[str, Any]:
        reserva = self.reserva_repo.get_by_id(id_reserva)
        if not reserva:
            raise ValueError("Reserva não encontrada.")
        if reserva.id_usuario != id_usuario:
            raise PermissionError("Usuário não autorizado a excluir esta reserva.")

        id_meta = reserva.id_meta
        self.reserva_repo.delete(id_reserva)
        meta_payload = self._recalcular_meta(id_meta)

        return {
            "meta": meta_payload,
            "mensagem": "Reserva removida e progresso da meta atualizado.",
        }


class ListarMetasDisponiveisParaReserva:
    def __init__(self, meta_repo: IMetaRepository):
        self.meta_repo = meta_repo

    def execute(self, id_usuario: str) -> Dict[str, Any]:
        metas = self.meta_repo.get_by_usuario(id_usuario)
        disponiveis = [meta for meta in metas if not meta.esta_concluida()]

        resposta = {
            "metas": [
                {
                    "id": meta.id,
                    "nome": meta.nome,
                    "valor_alvo": meta.valor_alvo,
                    "valor_atual": meta.valor_atual,
                    "progresso_percentual": meta.progresso_percentual(),
                    "data_limite": meta.data_limite.isoformat(),
                }
                for meta in disponiveis
            ]
        }

        if not disponiveis:
            resposta["mensagem"] = "Nenhuma meta disponível. Que tal criar uma nova meta agora?"

        return resposta
