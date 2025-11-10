from typing import List
from datetime import datetime
import sqlite3
from domain.meta import Meta
from use_cases.repository_interfaces import IMetaRepository


class MetaRepositorySqlite(IMetaRepository):
    """Repositório SQLite para Metas Financeiras."""

    def __init__(self, db_connection: sqlite3.Connection):
        self.db = db_connection

    def _map_row_to_meta(self, row: tuple) -> Meta:
        return Meta(
            id_usuario=row[1],
            nome=row[2],
            valor_alvo=row[3],
            valor_atual=row[4],
            data_limite=datetime.fromisoformat(row[5]) if row[5] else datetime.now(),
            id_perfil=row[6],
            id=row[0]
        )

    def add(self, meta: Meta) -> None:
        cursor = self.db.cursor()
        sql = """
        INSERT INTO meta (id, id_usuario, nome, valor_alvo, valor_atual, data_limite, id_perfil)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        cursor.execute(sql, (
            meta.id,
            meta.id_usuario,
            meta.nome,
            meta.valor_alvo,
            meta.valor_atual,
            meta.data_limite.isoformat(),
            meta.id_perfil
        ))
        self.db.commit()
        print(f"Repositório: Meta {meta.id} criada para usuário {meta.id_usuario}.")

    def get_by_usuario(self, id_usuario: str) -> List[Meta]:
        cursor = self.db.cursor()
        sql = """
        SELECT id, id_usuario, nome, valor_alvo, valor_atual, data_limite, id_perfil
        FROM meta
        WHERE id_usuario = ?
        ORDER BY data_limite ASC
        """
        cursor.execute(sql, (id_usuario,))
        rows = cursor.fetchall()
        return [self._map_row_to_meta(r) for r in rows]

    def update(self, meta: Meta) -> None:
        cursor = self.db.cursor()
        sql = """
        UPDATE meta
        SET nome = ?, valor_alvo = ?, valor_atual = ?, data_limite = ?, id_perfil = ?
        WHERE id = ?
        """
        cursor.execute(sql, (
            meta.nome,
            meta.valor_alvo,
            meta.valor_atual,
            meta.data_limite.isoformat(),
            meta.id_perfil,
            meta.id
        ))
        self.db.commit()
