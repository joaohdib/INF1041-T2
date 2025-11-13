from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import date
from domain.transacao import Transacao, StatusTransacao
from domain.meta import Meta
from domain.anexo import Anexo


# Os Casos de Uso dependem destas abstrações, não de implementações concretas.

class ITransacaoRepository(ABC):
    @abstractmethod
    def add(self, transacao: Transacao) -> None:
        pass

    @abstractmethod
    def get_pendentes_by_usuario(self, id_usuario: str) -> List[Transacao]:
        pass

    @abstractmethod
    def get_by_ids(self, ids_transacao: List[str]) -> List[Transacao]:
        pass
    
    @abstractmethod
    def update_batch(self, transacoes: List[Transacao]) -> None:
        pass

    @abstractmethod
    def get_dashboard_stats(self, id_usuario: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_by_id(self, id_transacao: str) -> Transacao | None:
        """ Busca uma transação única pelo seu ID. """
        pass

    @abstractmethod
    def get_by_filters(self, id_usuario: str, 
                       data_de: date | None = None, 
                       data_ate: date | None = None, 
                       valor_min: float | None = None, 
                       valor_max: float | None = None, 
                       descricao: str | None = None,
                       status: StatusTransacao | None = None) -> List[Transacao]:
        """ Busca transações com base em filtros dinâmicos. """
        pass


class IMetaRepository(ABC):
    @abstractmethod
    def add(self, meta: Meta) -> None:
        pass

    @abstractmethod
    def get_by_usuario(self, id_usuario: str) -> List[Meta]:
        pass

    @abstractmethod
    def update(self, meta: Meta) -> None:
        pass

class IAnexoRepository(ABC):
    """
    Interface de Repositório para metadados de Anexos.
    """
    @abstractmethod
    def add(self, anexo: Anexo) -> None:
        """ Adiciona os metadados de um novo anexo ao banco. """
        pass
    
    @abstractmethod
    def get_by_transacao_id(self, id_transacao: str) -> List[Anexo]:
        """ Lista todos os anexos de uma transação. """
        pass