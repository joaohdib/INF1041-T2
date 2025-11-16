from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import date
from domain.transacao import Transacao, StatusTransacao
from domain.meta import Meta
from domain.reserva import Reserva
from domain.anexo import Anexo
from domain.mapeamento_csv import MapeamentoCSV


# Os Casos de Uso dependem destas abstrações, não de implementações concretas.

class ITransacaoRepository(ABC):
    @abstractmethod
    def add(self, transacao: Transacao) -> None:
        pass

    @abstractmethod
    def update(self, transacao: Transacao) -> None:
        """ Atualiza uma transação existente. """
        pass

    @abstractmethod
    def delete(self, id_transacao: str) -> None:
        """ Deleta uma transação pelo ID. """
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
                       status: StatusTransacao | None = None,
                       id_categoria: str | None = None, # NOVO
                       id_perfil: str | None = None,    # NOVO
                       sem_categoria: bool = False,   # NOVO
                       sem_perfil: bool = False       # NOVO
                       ) -> List[Transacao]:
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

    @abstractmethod
    def get_by_id(self, id_meta: str) -> Meta | None:
        pass


class IReservaRepository(ABC):
    @abstractmethod
    def add(self, reserva: Reserva) -> None:
        pass

    @abstractmethod
    def update(self, reserva: Reserva) -> None:
        pass

    @abstractmethod
    def delete(self, reserva_id: str) -> None:
        pass

    @abstractmethod
    def get_by_id(self, reserva_id: str) -> Reserva | None:
        pass

    @abstractmethod
    def get_by_meta(self, id_meta: str) -> List[Reserva]:
        pass

    @abstractmethod
    def get_total_by_meta(self, id_meta: str) -> float:
        pass

class IAnexoRepository(ABC):
    """
    Interface de Repositório para metadados de Anexos.
    """
    @abstractmethod
    def add(self, anexo: Anexo) -> None:
        """ Adiciona os metadados de um novo anexo ao banco. """
        pass


class IMapeamentoCSVRepository(ABC):
    @abstractmethod
    def add(self, mapeamento: MapeamentoCSV) -> MapeamentoCSV:
        pass

    @abstractmethod
    def get_by_usuario(self, id_usuario: str) -> List[MapeamentoCSV]:
        pass

    @abstractmethod
    def get_by_id(self, id_mapeamento: str) -> MapeamentoCSV | None:
        pass

    @abstractmethod
    def exists_nome(self, id_usuario: str, nome: str) -> bool:
        pass
