from domain.transacao import StatusTransacao, TipoTransacao
from infra.db.database import Base
from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


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
    tipo = Column(Enum(TipoTransacao), nullable=False)


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
    concluida_em = Column(DateTime, nullable=True)
    finalizada_em = Column(DateTime, nullable=True)
    status = Column(String, nullable=False, default="ATIVA")  # ATIVA, PAUSADA, CONCLUIDA, CANCELADA

    id_perfil = Column(String, ForeignKey("perfil.id"), nullable=True)

    perfil = relationship("Perfil")
    reservas = relationship(
        "Reserva",
        back_populates="meta",
        cascade="all, delete-orphan",
    )
    usos = relationship(
        "MetaUso",
        back_populates="meta",
        cascade="all, delete-orphan",
    )


class Anexo(Base):
    __tablename__ = "anexo"
    id = Column(String, primary_key=True)
    id_transacao = Column(
        String, ForeignKey("transacao.id", ondelete="CASCADE"), nullable=False
    )
    nome_arquivo = Column(String, nullable=False)
    caminho_storage = Column(String, nullable=False)
    tipo_mime = Column(String, nullable=False)
    tamanho_bytes = Column(Integer, nullable=False)
    data_upload = Column(DateTime, nullable=False, server_default=func.now())

    transacao = relationship("Transacao")


class Reserva(Base):
    __tablename__ = "reserva"
    id = Column(String, primary_key=True)
    id_usuario = Column(String, nullable=False)
    id_meta = Column(String, ForeignKey("meta.id", ondelete="CASCADE"), nullable=False)
    valor = Column(Float, nullable=False)
    id_transacao = Column(
        String, ForeignKey("transacao.id", ondelete="SET NULL"), nullable=True
    )
    observacao = Column(Text, nullable=True)
    criado_em = Column(DateTime, nullable=False, server_default=func.now())
    atualizado_em = Column(DateTime, nullable=True, onupdate=func.now())

    meta = relationship("Meta", back_populates="reservas")
    transacao = relationship("Transacao", backref="reservas")


class MetaUso(Base):
    __tablename__ = "meta_uso"
    id = Column(String, primary_key=True)
    id_meta = Column(String, ForeignKey("meta.id", ondelete="CASCADE"), nullable=False)
    id_transacao = Column(
        String, ForeignKey("transacao.id", ondelete="CASCADE"), nullable=False
    )
    valor = Column(Float, nullable=False)
    criado_em = Column(DateTime, nullable=False, server_default=func.now())

    meta = relationship("Meta", back_populates="usos")
    transacao = relationship("Transacao")


class MapeamentoCSV(Base):
    __tablename__ = "mapeamento_csv"
    id = Column(String, primary_key=True)
    id_usuario = Column(String, nullable=False)
    nome = Column(String, nullable=False)
    coluna_data = Column(String, nullable=False)
    coluna_valor = Column(String, nullable=False)
    coluna_descricao = Column(String, nullable=False)
    criado_em = Column(DateTime, nullable=False, server_default=func.now())