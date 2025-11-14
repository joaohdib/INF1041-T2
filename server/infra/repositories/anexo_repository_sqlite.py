from typing import List
from sqlalchemy.orm import Session
from domain.anexo import Anexo as DomainAnexo
from use_cases.repository_interfaces import IAnexoRepository
from infra.db.models import Anexo as ModelAnexo

class AnexoRepositorySqlite(IAnexoRepository):
    """ Repositório SQLAlchemy para Anexos. """

    def __init__(self, db_session: Session):
        self.db = db_session

    def _map_model_to_domain(self, m_model: ModelAnexo) -> DomainAnexo:
        """Converte um Model do SQLAlchemy para uma Entidade de Domínio."""
        return DomainAnexo(
            id_transacao=m_model.id_transacao,
            nome_arquivo=m_model.nome_arquivo,
            caminho_storage=m_model.caminho_storage,
            tipo_mime=m_model.tipo_mime,
            tamanho_bytes=m_model.tamanho_bytes,
            id=m_model.id,
            data_upload=m_model.data_upload
        )

    def _map_domain_to_model(self, m_domain: DomainAnexo) -> ModelAnexo:
        """Converte uma Entidade de Domínio para um Model do SQLAlchemy."""
        return ModelAnexo(
            id=m_domain.id,
            id_transacao=m_domain.id_transacao,
            nome_arquivo=m_domain.nome_arquivo,
            caminho_storage=m_domain.caminho_storage,
            tipo_mime=m_domain.tipo_mime,
            tamanho_bytes=m_domain.tamanho_bytes,
            data_upload=m_domain.data_upload
        )

    def add(self, anexo: DomainAnexo) -> None:
        """ Adiciona os metadados do anexo ao banco de dados. """
        anexo_model = self._map_domain_to_model(anexo)
        self.db.add(anexo_model)
        # Commit é feito na camada de rota
        print(f"Repositório (SQLAlchemy): Adicionando anexo {anexo.id} para transação {anexo.id_transacao}.")

    def get_by_transacao_id(self, id_transacao: str) -> List[DomainAnexo]:
        """ Busca anexos por ID de transação. """
        rows_model = self.db.query(ModelAnexo).filter(
            ModelAnexo.id_transacao == id_transacao
        ).all()
        
        return [self._map_model_to_domain(row) for row in rows_model]