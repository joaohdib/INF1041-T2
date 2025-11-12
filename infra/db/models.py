from sqlalchemy import Column, String, Float, ForeignKey, DateTime, Enum, Integer
from sqlalchemy.orm import relationship
from infra.db.database import Base
from domain.transacao import TipoTransacao, StatusTransacao 
from domain.meta import Meta as DomainMeta
from domain.transacao import Transacao as DomainTransacao

# NOTA: Estes são os "Models de Infra", não as "Entidades de Domínio".
# Eles representam as TABELAS, não a regra de negócio.

class Perfil(Base):
    __tablename__ = "perfil"
    id = Column(String, primary_key=True)
    id_usuario = Column(String, nullable=False)
    nome = Column(String, nullable=False)

class Categoria(Base):
    __tablename__ = "categoria"
    id = Column(String, primary_key=True)
    id_usuario = Column(String, nullable=False)
    nome = Column(String, nullable=False)

class Transacao(Base):
    __tablename__ = "transacao"
    id = Column(String, primary_key=True)
    valor = Column(Float, nullable=False)
    tipo = Column(Enum(TipoTransacao), nullable=False)
    data = Column(DateTime, nullable=False)
    status = Column(Enum(StatusTransacao), nullable=False)
    id_usuario = Column(String, nullable=False)
    descricao = Column(String, nullable=True)
    
    id_categoria = Column(String, ForeignKey("categoria.id"), nullable=True)
    id_perfil = Column(String, ForeignKey("perfil.id"), nullable=True)
    id_projeto = Column(String, nullable=True) 

    # Relacionamentos (opcional, mas bom para queries futuras)
    categoria = relationship("Categoria")
    perfil = relationship("Perfil")

class Meta(Base):
    __tablename__ = "meta"
    id = Column(String, primary_key=True)
    id_usuario = Column(String, nullable=False)
    nome = Column(String, nullable=False)
    valor_alvo = Column(Float, nullable=False)
    valor_atual = Column(Float, default=0.0)
    data_limite = Column(DateTime, nullable=True)
    
    id_perfil = Column(String, ForeignKey("perfil.id"), nullable=True)
    
    perfil = relationship("Perfil")

class Anexo(Base):
    __tablename__ = "anexo"
    id = Column(String, primary_key=True)
    id_transacao = Column(String, ForeignKey("transacao.id", ondelete="CASCADE"), nullable=False)
    nome_arquivo = Column(String, nullable=False)
    caminho_storage = Column(String, nullable=False)
    tipo_mime = Column(String, nullable=False)
    tamanho_bytes = Column(Integer, nullable=False)
    
    transacao = relationship("Transacao")