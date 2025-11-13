from datetime import datetime
from typing import List

from sqlalchemy.orm import Session

from domain.meta import Meta
from infra.db.models import Meta as MetaModel
from use_cases.repository_interfaces import IMetaRepository


class MetaRepositorySqlite(IMetaRepository):
    """Repositório SQLAlchemy para Metas Financeiras."""

    def __init__(self, db_session: Session):
        self.db: Session = db_session

    def _map_model_to_meta(self, model: MetaModel) -> Meta:
        return Meta(
            id_usuario=model.id_usuario,
            nome=model.nome,
            valor_alvo=model.valor_alvo,
            valor_atual=model.valor_atual or 0.0,
            data_limite=model.data_limite or datetime.now(),
            id_perfil=model.id_perfil,
            id=model.id
        )

    def _map_meta_to_model(self, meta: Meta) -> MetaModel:
        return MetaModel(
            id=meta.id,
            id_usuario=meta.id_usuario,
            nome=meta.nome,
            valor_alvo=meta.valor_alvo,
            valor_atual=meta.valor_atual,
            data_limite=meta.data_limite,
            id_perfil=meta.id_perfil
        )

    def add(self, meta: Meta) -> None:
        meta_model = self._map_meta_to_model(meta)
        self.db.add(meta_model)
        print(f"Repositório (SQLAlchemy): Meta {meta.id} criada para usuário {meta.id_usuario}.")

    def get_by_usuario(self, id_usuario: str) -> List[Meta]:
        rows = (
            self.db
            .query(MetaModel)
            .filter(MetaModel.id_usuario == id_usuario)
            .order_by(MetaModel.data_limite.asc())
            .all()
        )
        return [self._map_model_to_meta(row) for row in rows]

    def update(self, meta: Meta) -> None:
        self.db.merge(self._map_meta_to_model(meta))
