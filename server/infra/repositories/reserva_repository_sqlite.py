from sqlalchemy.orm import Session
from sqlalchemy import func, delete

from domain.reserva import Reserva
from infra.db.models import Reserva as ReservaModel
from use_cases.repository_interfaces import IReservaRepository


class ReservaRepositorySqlite(IReservaRepository):
    """Repositório SQLAlchemy responsável pelas reservas vinculadas às metas."""

    def __init__(self, db_session: Session):
        self.db: Session = db_session

    def _map_model_to_reserva(self, model: ReservaModel) -> Reserva:
        return Reserva(
            id=model.id,
            id_usuario=model.id_usuario,
            id_meta=model.id_meta,
            valor=model.valor,
            id_transacao=model.id_transacao,
            observacao=model.observacao,
            criado_em=model.criado_em,
            atualizado_em=model.atualizado_em
        )

    def _map_reserva_to_model(self, reserva: Reserva) -> ReservaModel:
        return ReservaModel(
            id=reserva.id,
            id_usuario=reserva.id_usuario,
            id_meta=reserva.id_meta,
            valor=reserva.valor,
            id_transacao=reserva.id_transacao,
            observacao=reserva.observacao,
            criado_em=reserva.criado_em,
            atualizado_em=reserva.atualizado_em
        )

    def add(self, reserva: Reserva) -> None:
        self.db.add(self._map_reserva_to_model(reserva))
        self.db.flush()

    def update(self, reserva: Reserva) -> None:
        self.db.merge(self._map_reserva_to_model(reserva))
        self.db.flush()

    def delete(self, reserva_id: str) -> None:
        self.db.execute(delete(ReservaModel).where(ReservaModel.id == reserva_id))
        self.db.flush()

    def get_by_id(self, reserva_id: str) -> Reserva | None:
        row = self.db.query(ReservaModel).filter(ReservaModel.id == reserva_id).first()
        if not row:
            return None
        return self._map_model_to_reserva(row)

    def get_by_meta(self, id_meta: str):
        rows = self.db.query(ReservaModel).filter(ReservaModel.id_meta == id_meta).order_by(ReservaModel.criado_em.asc()).all()
        return [self._map_model_to_reserva(row) for row in rows]

    def get_total_by_meta(self, id_meta: str) -> float:
        total = (
            self.db
            .query(func.coalesce(func.sum(ReservaModel.valor), 0.0))
            .filter(ReservaModel.id_meta == id_meta)
            .scalar()
        )
        return float(total or 0.0)
