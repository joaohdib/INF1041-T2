from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import date
from domain.transacao import Transacao, StatusTransacao
from domain.meta import Meta
from domain.reserva import Reserva
from domain.anexo import Anexo


class ITransacaoRepository(ABC):
    @abstractmethod
    def add(self, transacao: Transacao) -> None:
        pass

    @abstractmethod
    def update(self, transacao: Transacao) -> None:
        pass

    @abstractmethod
    def delete(self, id_transacao: str) -> None:
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
        pass

    @abstractmethod
    def get_by_filters(self, id_usuario: str, 
                       data_de: date | None = None, 
                       data_ate: date | None = None, 
                       valor_min: float | None = None, 
                       valor_max: float | None = None, 
                       descricao: str | None = None,
                       status: StatusTransacao | None = None,
                       id_categoria: str | None = None,
                       id_perfil: str | None = None,
                       sem_categoria: bool = False,
                       sem_perfil: bool = False
                       ) -> List[Transacao]:
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

    @abstractmethod
    def sum_reservas(self, id_meta: str) -> float:
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
    @abstractmethod
    def add(self, anexo: Anexo) -> None:
        pass
    
    @abstractmethod
    def get_by_transacao_id(self, id_transacao: str) -> List[Anexo]:
        pass

class IMetaUsoRepository(ABC):
    @abstractmethod
    def add_uso(self, id_meta: str, id_transacao: str, valor: float) -> Any:
        pass

    @abstractmethod
    def get_transacao(self, id_transacao: str) -> Any:
        pass

    @abstractmethod
    def sum_uso_por_meta(self, id_meta: str) -> float:
        pass

    @abstractmethod
    def get_usos_por_meta(self, id_meta: str) -> List[Any]:
        pass