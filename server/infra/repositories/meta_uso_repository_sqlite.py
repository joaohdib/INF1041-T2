import uuid

from sqlalchemy import func
from sqlalchemy.orm import Session

from infra.db.models import MetaUso as MetaUsoModel
from use_cases.repository_interfaces import IMetaUsoRepository


class MetaUsoRepositorySqlite(IMetaUsoRepository):
    def __init__(self, db_session: Session):
        self.db = db_session

    def add_uso(self, id_meta: str, id_transacao: str, valor: float) -> MetaUsoModel:
        meta_uso = MetaUsoModel(
            id=str(uuid.uuid4()),
            id_meta=id_meta,
            id_transacao=id_transacao,
            valor=valor
        )
        self.db.add(meta_uso)
        return meta_uso

    def sum_uso_por_meta(self, id_meta: str) -> float:
        total = self.db.query(MetaUsoModel).filter(
            MetaUsoModel.id_meta == id_meta
        ).with_entities(
            func.coalesce(func.sum(MetaUsoModel.valor), 0.0)
        ).scalar()
        return float(total or 0.0)

    def get_usos_por_meta(self, id_meta: str):
        return self.db.query(MetaUsoModel).filter(
            MetaUsoModel.id_meta == id_meta
        ).all()
