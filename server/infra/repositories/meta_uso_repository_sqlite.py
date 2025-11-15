from sqlalchemy.orm import Session
from sqlalchemy import func
from infra.db.models import MetaUso as MetaUsoModel
from use_cases.repository_interfaces import IMetaUsoRepository
from infra.repositories.transacao_repository_sqlite import TransacaoRepositorySqlite

class MetaUsoRepositorySqlite(IMetaUsoRepository):
    def __init__(self, db_session: Session):
        self.db = db_session
        self.transacao_repo = TransacaoRepositorySqlite(db_session)

    def add_uso(self, id_meta: str, id_transacao: str, valor: float) -> MetaUsoModel:
        meta_uso = MetaUsoModel(
            id_meta=id_meta,
            id_transacao=id_transacao,
            valor=valor
        )
        self.db.add(meta_uso)
        return meta_uso

    def get_transacao(self, id_transacao: str):
        return self.transacao_repo.get_by_id(id_transacao)

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