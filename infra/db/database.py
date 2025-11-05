import sqlite3
import os

# Define o nome do arquivo do banco de dados
DATABASE_FILE = "plano.db"

def get_db_connection():
    """
    Cria e retorna uma conexão com o banco de dados SQLite.
    Esta é a função que será injetada nos repositórios.
    """
    # Se o 'g' (contexto global do Flask) existir, reutiliza a conexão.
    # Senão, cria uma nova. (Isso será útil quando integrarmos com main.py)
    # Por enquanto, vamos manter simples:
    
    conn = sqlite3.connect(DATABASE_FILE)
    
    # Habilitar chaves estrangeiras é crucial para a integridade dos dados
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def create_tables(connection):
    """
    Executa os comandos SQL para criar o schema inicial do banco.
    """
    cursor = connection.cursor()
    
    # --- Tabelas Principais (Entidades de Domínio) ---
    
    # Tabela de Usuário (implícita, mas necessária para FKs)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuario (
        id TEXT PRIMARY KEY,
        nome TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL
    )
    """)
    
    # Tabela de Perfil (Pessoal, PJ, etc.)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS perfil (
        id TEXT PRIMARY KEY,
        id_usuario TEXT NOT NULL,
        nome TEXT NOT NULL,
        FOREIGN KEY (id_usuario) REFERENCES usuario (id)
    )
    """)
    
    # Tabela de Categoria (Alimentação, Transporte, etc.)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS categoria (
        id TEXT PRIMARY KEY,
        id_usuario TEXT NOT NULL,
        nome TEXT NOT NULL,
        FOREIGN KEY (id_usuario) REFERENCES usuario (id)
    )
    """)
    
    # Tabela de Projeto (Cliente A, Projeto X, etc.)
    # (Implícita pelo 'id_projeto' na Transacao)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS projeto (
        id TEXT PRIMARY KEY,
        id_usuario TEXT NOT NULL,
        nome TEXT NOT NULL,
        FOREIGN KEY (id_usuario) REFERENCES usuario (id)
    )
    """)

    # Tabela de Transação (O coração da sua funcionalidade)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transacao (
        id TEXT PRIMARY KEY,
        valor REAL NOT NULL,
        tipo TEXT NOT NULL,             -- "RECEITA" ou "DESPESA"
        data TEXT NOT NULL,             -- Data em formato ISO (string)
        status TEXT NOT NULL,           -- "PENDENTE" ou "PROCESSADO"
        id_usuario TEXT NOT NULL,
        descricao TEXT,
        id_categoria TEXT,
        id_perfil TEXT,
        id_projeto TEXT,
        CHECK (valor > 0),
        CHECK (tipo IN ('RECEITA', 'DESPESA')),
        CHECK (status IN ('PENDENTE', 'PROCESSADO')),
        FOREIGN KEY (id_usuario) REFERENCES usuario (id),
        FOREIGN KEY (id_categoria) REFERENCES categoria (id),
        FOREIGN KEY (id_perfil) REFERENCES perfil (id),
        FOREIGN KEY (id_projeto) REFERENCES projeto (id)
    )
    """)
    
    # Tabela de Anexo (para PPI-12)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS anexo (
        id TEXT PRIMARY KEY,
        id_transacao TEXT NOT NULL,
        nome_arquivo TEXT NOT NULL,
        caminho_storage TEXT NOT NULL,  -- (ex: 'uploads/abc.pdf')
        tipo_mime TEXT NOT NULL,
        tamanho_bytes INTEGER NOT NULL,
        FOREIGN KEY (id_transacao) REFERENCES transacao (id) ON DELETE CASCADE
    )
    """)
    
    # Tabela de Meta (para a outra equipe)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS meta (
        id TEXT PRIMARY KEY,
        id_usuario TEXT NOT NULL,
        nome TEXT NOT NULL,
        valor_alvo REAL NOT NULL,
        valor_atual REAL DEFAULT 0.0,
        data_limite TEXT,               -- Data em formato ISO (string)
        FOREIGN KEY (id_usuario) REFERENCES usuario (id)
    )
    """)
    
    print("Tabelas verificadas/criadas com sucesso.")
    connection.commit()

def init_db():
    """
    Função principal de inicialização.
    Verifica se o DB existe, se não, cria e popula as tabelas.
    """
    # Verifica se o arquivo .db já existe
    db_exists = os.path.exists(DATABASE_FILE)
    
    conn = get_db_connection()
    try:
        if not db_exists:
            print(f"Criando novo banco de dados em: {DATABASE_FILE}")
        
        create_tables(conn)
        
    except sqlite3.Error as e:
        print(f"Erro ao inicializar o banco de dados: {e}")
        
    finally:
        conn.close()

if __name__ == "__main__":
    """
    Permite executar este script diretamente (python infra/db/database.py)
    para criar o banco de dados pela primeira vez.
    """
    print("Inicializando o banco de dados...")
    init_db()
    print("Banco de dados pronto.")

