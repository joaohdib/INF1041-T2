from domain.transacao import Transacao, TipoTransacao, StatusTransacao
from use_cases.repository_interfaces import ITransacaoRepository
from typing import List, Dict, Any
from datetime import datetime
import sqlite3

class TransacaoRepositorySqlite(ITransacaoRepository):
    
    def __init__(self, db_connection):
        self.db = db_connection

    def _map_row_to_transacao(self, row: tuple) -> Transacao:
        """
        Função auxiliar para converter uma linha do banco de dados 
        (que é uma tupla) em um objeto de domínio Transacao.
        """
        # A ordem das colunas deve bater com o SELECT
        return Transacao(
            id=row[0],
            valor=row[1],
            # Converte a string do DB de volta para o Enum
            tipo=TipoTransacao(row[2]), 
            # Converte a string ISO de volta para um objeto datetime
            data=datetime.fromisoformat(row[3]), 
            status=StatusTransacao(row[4]),
            id_usuario=row[5],
            descricao=row[6],
            id_categoria=row[7],
            id_perfil=row[8],
            id_projeto=row[9]
        )

    def add(self, transacao: Transacao) -> None:
        """
        Implementa o INSERT para o PPI-9 (Lançar Transação).
        """
        cursor = self.db.cursor()
        sql = """
        INSERT INTO transacao 
            (id, valor, tipo, data, status, id_usuario, descricao, 
             id_categoria, id_perfil, id_projeto)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        # Converte o objeto Transacao em uma tupla para o SQL
        data_tuple = (
            transacao.id,
            transacao.valor,
            transacao.tipo.value,       # Armazena o valor do Enum (ex: "DESPESA")
            transacao.data.isoformat(), # Armazena data como string ISO
            transacao.status.value,
            transacao.id_usuario,
            transacao.descricao,
            transacao.id_categoria,
            transacao.id_perfil,
            transacao.id_projeto
        )
        
        cursor.execute(sql, data_tuple)
        self.db.commit()
        print(f"Repositório: Salvando transação {transacao.id} no SQLite.")

    def get_pendentes_by_usuario(self, id_usuario: str) -> List[Transacao]:
        """
        Implementa o SELECT para o PPI-10 (Listar Inbox).
        Busca transações PENDENTES (que ainda não foram categorizadas).
        """
        print(f"Repositório: Buscando transações pendentes (Inbox) para {id_usuario}.")
        cursor = self.db.cursor()
        # Define quais colunas e em que ordem
        sql = """
        SELECT id, valor, tipo, data, status, id_usuario, descricao, 
               id_categoria, id_perfil, id_projeto
        FROM transacao
        WHERE id_usuario = ? AND status = ?
        ORDER BY data DESC
        """
        
        cursor.execute(sql, (id_usuario, StatusTransacao.PENDENTE.value))
        rows = cursor.fetchall()
        
        # Mapeia as linhas (tuplas) de volta para objetos Transacao
        return [self._map_row_to_transacao(row) for row in rows]

    def get_by_ids(self, ids_transacao: List[str]) -> List[Transacao]:
        """
        Implementa o SELECT...IN para o PPI-11 (Ação em Massa).
        Busca um conjunto de transações pelos seus IDs.
        """
        print(f"Repositório: Buscando transações {ids_transacao} para ação em massa.")
        if not ids_transacao:
            return []
            
        # Cria os placeholders (?) dinamicamente para a cláusula IN
        # Ex: "WHERE id IN (?, ?, ?)"
        placeholders = ','.join('?' for _ in ids_transacao)
        
        sql = f"""
        SELECT id, valor, tipo, data, status, id_usuario, descricao, 
               id_categoria, id_perfil, id_projeto
        FROM transacao
        WHERE id IN ({placeholders})
        """
        
        cursor = self.db.cursor()
        cursor.execute(sql, ids_transacao)
        rows = cursor.fetchall()
        
        return [self._map_row_to_transacao(row) for row in rows]
    
    def update_batch(self, transacoes: List[Transacao]) -> None:
        """
        Implementa o UPDATE em lote para o PPI-11 (Categorizar em Massa).
        Atualiza o status, categoria e perfil das transações.
        """
        print(f"Repositório: Atualizando {len(transacoes)} transações em massa.")
        if not transacoes:
            return

        sql = """
        UPDATE transacao
        SET status = ?, id_categoria = ?, id_perfil = ?
        WHERE id = ?
        """
        
        # Cria uma lista de tuplas para o método 'executemany'
        # (status, categoria, perfil, id)
        data_tuples = [
            (
                t.status.value,
                t.id_categoria,
                t.id_perfil,
                t.id  # ID para a cláusula WHERE
            ) for t in transacoes
        ]
        
        cursor = self.db.cursor()
        cursor.executemany(sql, data_tuples)
        self.db.commit()
    
    def get_dashboard_stats(self, id_usuario: str) -> Dict[str, Any]:
        """
        Implementa a agregação SQL para os cards do Dashboard (Wireframes).
        Calcula saldo total, receitas do mês e despesas do mês.
        
        NOTA: Esta consulta considera APENAS transações PROCESSADAS (confirmadas).
        """
        print(f"Repositório: Calculando estatísticas do dashboard para {id_usuario}.")
        
        # Calcula o primeiro dia do mês atual para os filtros
        today = datetime.now()
        start_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()

        sql = """
        SELECT
            -- Saldo Atual (Total de Receitas - Total de Despesas)
            COALESCE(SUM(CASE WHEN tipo = 'RECEITA' THEN valor ELSE -valor END), 0) as saldo_atual,
            
            -- Receitas do Mês (Soma de Receitas >= início do mês)
            COALESCE(SUM(CASE WHEN tipo = 'RECEITA' AND data >= ? THEN valor ELSE 0 END), 0) as receitas_mes,
            
            -- Despesas do Mês (Soma de Despesas >= início do mês)
            COALESCE(SUM(CASE WHEN tipo = 'DESPESA' AND data >= ? THEN valor ELSE 0 END), 0) as despesas_mes
        FROM transacao
        WHERE id_usuario = ? AND status = ? 
        """
        
        cursor = self.db.cursor()
        cursor.execute(sql, (
            start_of_month, 
            start_of_month, 
            id_usuario, 
            StatusTransacao.PROCESSADO.value # Apenas transações confirmadas
        ))
        
        result = cursor.fetchone()
        
        if result:
            return {
                "saldo_atual": result[0],
                "receitas_mes": result[1],
                "despesas_mes": result[2]
            }
        
        # Caso não retorne nada (usuário novo)
        return {"saldo_atual": 0.0, "receitas_mes": 0.0, "despesas_mes": 0.0}