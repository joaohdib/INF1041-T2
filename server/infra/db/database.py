import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base

# Adiciona o diretório raiz ao path para encontrar o 'domain'
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Define o nome do arquivo do banco de dados
DATABASE_FILE = "plano.db"
DATABASE_URL = f"sqlite:///{DATABASE_FILE}"

# 1. Engine: O "conector" principal
# connect_args={"check_same_thread": False} é necessário para o SQLite com Flask
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# 2. Session Factory: Fábrica de sessões (transações)
# scoped_session garante que cada request web tenha sua própria sessão isolada
session_factory = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Session = scoped_session(session_factory)

# 3. Base: A classe base para todos os seus "Models" (tabelas)
Base = declarative_base()

def get_db_session():
    """
    Retorna uma nova sessão do SQLAlchemy.
    Será injetada nos repositórios.
    """
    return Session()

def init_db():
    """
    Função principal de inicialização.
    Importa os models e cria todas as tabelas no banco de dados.
    """
    try:
        print("Inicializando o banco de dados (SQLAlchemy)...")
        # Importa os models aqui para que eles sejam registrados pela Base
        from infra.db import models 
        
        # Cria as tabelas com base nos Models que herdam de Base
        Base.metadata.create_all(bind=engine)
        print("Tabelas criadas com sucesso.")
    except Exception as e:
        print(f"ERRO: Não foi possível inicializar o banco de dados.")
        print(f"Detalhe: {e}")
        sys.exit(1)

if __name__ == "__main__":
    """
    Permite executar este script diretamente para criar o banco de dados pela 
    primeira vez.
    """
    print("Inicializando o banco de dados...")
    init_db()
    print("Banco de dados pronto.")

