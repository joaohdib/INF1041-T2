from sqlalchemy.orm import Session

from domain.mapeamento_csv import MapeamentoCSV as DomainMapeamento
from infra.db.models import MapeamentoCSV as ModelMapeamento
from use_cases.repository_interfaces import IMapeamentoCSVRepository


class MapeamentoCSVRepositorySqlite(IMapeamentoCSVRepository):
    def __init__(self, db_session: Session):
        self.db = db_session

    def _model_to_domain(self, model: ModelMapeamento) -> DomainMapeamento | None:
        if not model:
            return None
        return DomainMapeamento(
            id=model.id,
            id_usuario=model.id_usuario,
            nome=model.nome,
            coluna_data=model.coluna_data,
            coluna_valor=model.coluna_valor,
            coluna_descricao=model.coluna_descricao,
        )

    def add(self, mapeamento: DomainMapeamento) -> DomainMapeamento:
        model = ModelMapeamento(
            id=mapeamento.id,
            id_usuario=mapeamento.id_usuario,
            nome=mapeamento.nome,
            coluna_data=mapeamento.coluna_data,
            coluna_valor=mapeamento.coluna_valor,
            coluna_descricao=mapeamento.coluna_descricao,
        )
        self.db.add(model)
        self.db.flush()
        return mapeamento

    def get_by_usuario(self, id_usuario: str) -> list[DomainMapeamento]:
        rows = (
            self.db.query(ModelMapeamento)
            .filter(ModelMapeamento.id_usuario == id_usuario)
            .order_by(ModelMapeamento.nome.asc())
            .all()
        )
        return [self._model_to_domain(row) for row in rows]

    def get_by_id(self, id_mapeamento: str) -> DomainMapeamento | None:
        model = self.db.query(ModelMapeamento).filter_by(id=id_mapeamento).first()
        return self._model_to_domain(model)

    def exists_nome(self, id_usuario: str, nome: str) -> bool:
        return (
            self.db.query(ModelMapeamento)
            .filter(
                ModelMapeamento.id_usuario == id_usuario,
                ModelMapeamento.nome == nome,
            )
            .first()
            is not None
        )
