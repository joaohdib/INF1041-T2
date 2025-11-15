from datetime import datetime
from typing import List

from sqlalchemy import func
from sqlalchemy.orm import Session

from domain.meta import Meta
from infra.db.models import Meta as MetaModel
from use_cases.repository_interfaces import IMetaRepository


class MetaRepositorySqlite(IMetaRepository):
    def __init__(self, db_session: Session):
        self.db: Session = db_session

    def _map_model_to_meta(self, model: MetaModel) -> Meta:
        return Meta(
            id_usuario=model.id_usuario,
            nome=model.nome,
            valor_alvo=model.valor_alvo,
            valor_atual=model.valor_atual or 0.0,
            data_limite=model.data_limite,
            id_perfil=model.id_perfil,
            concluida_em=model.concluida_em,
            finalizada_em=model.finalizada_em,
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
            id_perfil=meta.id_perfil,
            concluida_em=meta.concluida_em,
            finalizada_em=meta.finalizada_em
        )

    def add(self, meta: Meta) -> None:
        meta_model = self._map_meta_to_model(meta)
        self.db.add(meta_model)
        print(f"Repositório: Meta {meta.id} criada")

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
        # Busca a meta existente no banco
        meta_existente = self.db.query(MetaModel).filter(MetaModel.id == meta.id).first()
        if not meta_existente:
            raise ValueError(f"Meta {meta.id} não encontrada para atualização")
        
        # Atualiza os campos
        meta_existente.nome = meta.nome
        meta_existente.valor_alvo = meta.valor_alvo
        meta_existente.valor_atual = meta.valor_atual
        meta_existente.data_limite = meta.data_limite
        meta_existente.id_perfil = meta.id_perfil
        meta_existente.concluida_em = meta.concluida_em
        meta_existente.finalizada_em = meta.finalizada_em
        
        print(f"Repositório: Meta {meta.id} atualizada - concluida_em: {meta.concluida_em}, finalizada_em: {meta.finalizada_em}")

    def get_by_id(self, id_meta: str) -> Meta | None:
        row = self.db.query(MetaModel).filter(MetaModel.id == id_meta).first()
        if not row:
            return None
        meta = self._map_model_to_meta(row)
        print(f"Repositório: Meta {meta.id} recuperada - concluida: {meta.esta_concluida()}, finalizada: {meta.esta_finalizada()}")
        return meta

    def sum_reservas(self, id_meta: str) -> float:
        from infra.db.models import Reserva as ReservaModel

        total = (
            self.db
            .query(ReservaModel)
            .with_entities(func.coalesce(func.sum(ReservaModel.valor), 0.0))
            .filter(ReservaModel.id_meta == id_meta)
            .scalar()
        )
        return float(total or 0.0)