from abc import ABC, abstractmethod
from typing import List, Dict, Any
from domain.transacao import Transacao

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