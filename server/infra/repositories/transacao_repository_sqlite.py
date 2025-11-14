from sqlalchemy.orm import Session
from sqlalchemy import func, case, delete
from typing import List, Dict, Any
from datetime import datetime, date

# Entidades de Domínio (o "contrato" do repositório)
from domain.transacao import Transacao as DomainTransacao
from domain.transacao import TipoTransacao, StatusTransacao

# Interfaces (para garantir conformidade)
from use_cases.repository_interfaces import ITransacaoRepository

# Models de Infra (a tabela do banco)
from infra.db.models import Transacao as ModelTransacao

class TransacaoRepositorySqlite(ITransacaoRepository):
    
    def __init__(self, db_session: Session):
        # Recebemos a SESSÃO do SQLAlchemy, não a conexão
        self.db: Session = db_session

    # --- Funções Auxiliares de Mapeamento ---
    # O Repositório é o tradutor oficial entre o Domínio e a Infra

    def _map_model_to_domain(self, t_model: ModelTransacao) -> DomainTransacao:
        """Converte um Model do SQLAlchemy para uma Entidade de Domínio."""
        if not t_model:
            return None
        return DomainTransacao(
            id=t_model.id,
            valor=t_model.valor,
            tipo=t_model.tipo,
            data=t_model.data,
            status=t_model.status,
            id_usuario=t_model.id_usuario,
            descricao=t_model.descricao,
            id_categoria=t_model.id_categoria,
            id_perfil=t_model.id_perfil,
            id_projeto=t_model.id_projeto
        )
    
    def _map_domain_to_model(self, t_domain: DomainTransacao) -> ModelTransacao:
        """Converte uma Entidade de Domínio para um Model do SQLAlchemy."""
        # Cria um novo objeto Model com os dados do Domínio
        return ModelTransacao(
            id=t_domain.id,
            valor=t_domain.valor,
            tipo=t_domain.tipo,
            data=t_domain.data,
            status=t_domain.status,
            id_usuario=t_domain.id_usuario,
            descricao=t_domain.descricao,
            id_categoria=t_domain.id_categoria,
            id_perfil=t_domain.id_perfil,
            id_projeto=t_domain.id_projeto
        )
    
    # --- Implementação da Interface ---

    def add(self, transacao: DomainTransacao) -> None:
        """ Implementa o INSERT com SQLAlchemy. """
        # 1. Traduzir do Domínio para o Model de Infra
        transacao_model = self._map_domain_to_model(transacao)
        
        # 2. Usar a sessão do SQLAlchemy
        self.db.add(transacao_model)

        # O commit será feito na camada de Rota
        print(f"Repositório (SQLAlchemy): Adicionando transação {transacao.id}.")
    
    def update(self, transacao: DomainTransacao) -> None:
        """ Atualiza uma transação usando merge. """
        # O merge é ideal pois ele insere ou atualiza baseado na PK
        transacao_model = self._map_domain_to_model(transacao)
        self.db.merge(transacao_model)
        print(f"Repositório (SQLAlchemy): Atualizando transação {transacao.id}.")

    def delete(self, id_transacao: str) -> None:
        """ Deleta uma transação pelo ID. """
        # Cria a instrução de delete
        stmt = delete(ModelTransacao).where(ModelTransacao.id == id_transacao)
        self.db.execute(stmt)
        print(f"Repositório (SQLAlchemy): Deletando transação {id_transacao}.")

    def get_pendentes_by_usuario(self, id_usuario: str) -> List[DomainTransacao]:
        """ Implementa o SELECT (Listar Inbox). """
        print(f"Repositório (SQLAlchemy): Buscando transações pendentes para {id_usuario}.")
        
        rows_model = self.db.query(ModelTransacao).filter(
            ModelTransacao.id_usuario == id_usuario,
            ModelTransacao.status == StatusTransacao.PENDENTE
        ).order_by(ModelTransacao.data.desc()).all()
        
        # Mapeia os Models (Infra) de volta para Entidades (Domínio)
        return [self._map_model_to_domain(row) for row in rows_model]

    def get_by_ids(self, ids_transacao: List[str]) -> List[DomainTransacao]:
        """ Implementa o SELECT...IN(Ação em Massa). """
        print(f"Repositório (SQLAlchemy): Buscando transações {ids_transacao}.")
        if not ids_transacao:
            return []
            
        rows_model = self.db.query(ModelTransacao).filter(
            ModelTransacao.id.in_(ids_transacao)
        ).all()
        
        return [self._map_model_to_domain(row) for row in rows_model]
    
    def update_batch(self, transacoes: List[DomainTransacao]) -> None:
        """ Implementa o UPDATE em lote (Categorizar em Massa). """
        print(f"Repositório (SQLAlchemy): Atualizando {len(transacoes)} transações.")
        if not transacoes:
            return

        for t_domain in transacoes:
            # O 'merge' atualiza um objeto existente na sessão (baseado na PK)
            t_model = self._map_domain_to_model(t_domain)
            self.db.merge(t_model)
    
    def get_dashboard_stats(self, id_usuario: str) -> Dict[str, Any]:
        """ Implementa a agregação SQL para os cards do Dashboard. """
        print(f"Repositório (SQLAlchemy): Calculando estatísticas para {id_usuario}.")

        today = datetime.now()
        start_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Expressão de valor (positivo para receita, negativo para despesa)
        valor_calculado = case(
            (ModelTransacao.tipo == TipoTransacao.RECEITA, ModelTransacao.valor),
            else_=-ModelTransacao.valor
        )
        
        # Filtros base
        query_base = self.db.query(ModelTransacao).filter(
            ModelTransacao.id_usuario == id_usuario,
            ModelTransacao.status == StatusTransacao.PROCESSADO
        )
        
        # Saldo total (sem filtro de data)
        saldo_atual = query_base.with_entities(func.sum(valor_calculado)).scalar()
        
        # Filtros de data (apenas para estatísticas do mês)
        query_mes_atual = query_base.filter(ModelTransacao.data >= start_of_month)
        
        receitas_mes = query_mes_atual.with_entities(
            func.sum(case((ModelTransacao.tipo == TipoTransacao.RECEITA, ModelTransacao.valor), else_=0))
        ).scalar()
        
        despesas_mes = query_mes_atual.with_entities(
            func.sum(case((ModelTransacao.tipo == TipoTransacao.DESPESA, ModelTransacao.valor), else_=0))
        ).scalar()

        return {
            "saldo_atual": saldo_atual or 0.0,
            "receitas_mes": receitas_mes or 0.0,
            "despesas_mes": despesas_mes or 0.0
        }
    
    def get_by_id(self, id_transacao: str) -> DomainTransacao | None:
        """ Busca uma transação única pelo seu ID. """
        model = self.db.query(ModelTransacao).filter_by(id=id_transacao).first()
        return self._map_model_to_domain(model)
    
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
                       ) -> List[DomainTransacao]:
        
        print(f"Repositório (SQLAlchemy): Buscando transações com filtros avançados.")
        
        query = self.db.query(ModelTransacao).filter(
            ModelTransacao.id_usuario == id_usuario
        )

        if status:
            query = query.filter(ModelTransacao.status == status)
        
        if data_de:
            start_of_day = datetime.combine(data_de, datetime.min.time())
            query = query.filter(ModelTransacao.data >= start_of_day)

        if data_ate:
            end_of_day = datetime.combine(data_ate, datetime.max.time())
            query = query.filter(ModelTransacao.data <= end_of_day)

        if valor_min is not None:
            query = query.filter(ModelTransacao.valor >= valor_min)

        if valor_max is not None:
            query = query.filter(ModelTransacao.valor <= valor_max)
            
        if descricao:
            query = query.filter(ModelTransacao.descricao.like(f"%{descricao}%"))
        
        
        if id_categoria:
            query = query.filter(ModelTransacao.id_categoria == id_categoria)
        elif sem_categoria:
           
            query = query.filter(ModelTransacao.id_categoria == None)
            
        if id_perfil:
            query = query.filter(ModelTransacao.id_perfil == id_perfil)
        elif sem_perfil:
            
            query = query.filter(ModelTransacao.id_perfil == None)
       

        rows_model = query.order_by(
            ModelTransacao.status.asc(), 
            ModelTransacao.data.desc()
        ).all()
        return [self._map_model_to_domain(row) for row in rows_model]
