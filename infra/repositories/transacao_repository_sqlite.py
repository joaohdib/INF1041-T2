from domain.transacao import Transacao
from use_cases.repository_interfaces import ITransacaoRepository
from typing import List, Dict, Any


class TransacaoRepositorySqlite(ITransacaoRepository):
    
    def __init__(self, db_connection):
        self.db = db_connection

    def add(self, transacao: Transacao) -> None:
        cursor = self.db.cursor()
        # TODO
        # SQL para INSERIR a transação...
        # cursor.execute(...)
        self.db.commit()
        print(f"Repositório: Salvando transação {transacao.id} no SQLite.")
        pass

    def get_pendentes_by_usuario(self, id_usuario: str) -> List[Transacao]:
        print(f"Repositório: Buscando transações pendentes (Inbox) para {id_usuario}.")
        # TODO
        # SQL para SELECT ... WHERE status = 'PENDENTE'
        return []

    def get_by_ids(self, ids_transacao: List[str]) -> List[Transacao]:
        print(f"Repositório: Buscando transações {ids_transacao} para ação em massa.")
        # TODO
        return []
    
    def update_batch(self, transacoes: List[Transacao]) -> None:
        print(f"Repositório: Atualizando {len(transacoes)} transações em massa.")
        # TODO
        # SQL para UPDATE em lote...
        pass
    
    def get_dashboard_stats(self, id_usuario: str) -> Dict[str, Any]:
        print(f"Repositório: Calculando estatísticas do dashboard para {id_usuario}.")
        # TODO
        # SQL para calcular Saldo, Receitas, Despesas...
        return {"saldo_atual": 1000.0, "receitas_mes": 500.0, "despesas_mes": 250.0}