from datetime import datetime, date
from typing import List, Dict, Any
from domain.transacao import Transacao, TipoTransacao, StatusTransacao
from domain.anexo import Anexo
from use_cases.repository_interfaces import (
    ITransacaoRepository, 
    IAnexoRepository
)
from infra.storage.storage_interface import IAnexoStorage
import mimetypes


class LancarTransacao:
    def __init__(self, transacao_repo: ITransacaoRepository):
        self.transacao_repo = transacao_repo

    def execute(self, id_usuario: str, valor: float, tipo: str, 
                data: datetime | None = None, 
                descricao: str | None = None,
                id_categoria: str | None = None, # NOVO
                id_perfil: str | None = None      # NOVO
                ) -> Transacao:
        
        # 1. Validação de regras de negócio
        if valor <= 0:
            raise ValueError("O valor deve ser maior que zero.")
        
        # Se for um lançamento completo (com categoria/perfil), pula a Inbox.
        if id_categoria and id_perfil:
            status = StatusTransacao.PROCESSADO
        else:
            # Se for um lançamento rápido (sem detalhes), cai na Inbox.
            status = StatusTransacao.PENDENTE
            
        # 2. Criação da entidade
        transacao = Transacao(
            id_usuario=id_usuario,
            valor=valor,
            tipo=TipoTransacao(tipo.upper()),
            data=data or datetime.now(),
            descricao=descricao,
            status=status,  
            id_categoria=id_categoria, 
            id_perfil=id_perfil 
        )
        
        # 3. Persistência
        self.transacao_repo.add(transacao)
        return transacao
    

class AnexarReciboTransacao:
    """
    Caso de Uso: Anexar foto do recibo.
    Implementação finalizada.
    """
    # Limites (5MB) - Cenário de Falha
    MAX_SIZE_BYTES = 5 * 1024 * 1024
    # Cenário de Falha
    ALLOWED_MIMES = ["image/jpeg", "image/png", "application/pdf"]

    def __init__(self, storage: IAnexoStorage, 
                 anexo_repo: IAnexoRepository, 
                 transacao_repo: ITransacaoRepository):
        self.storage = storage
        self.anexo_repo = anexo_repo
        self.transacao_repo = transacao_repo

    def execute(self, id_usuario: str, id_transacao: str, 
                file_stream: Any, file_name: str, 
                content_type: str, content_length: int) -> Anexo:
        
        # 1. Validações do arquivo (Cenários de Falha)
        if content_type not in self.ALLOWED_MIMES:
            raise ValueError(f"Formato de arquivo não suportado: {content_type}. (Permitidos: JPG, PNG, PDF)")
        
        if content_length > self.MAX_SIZE_BYTES:
            raise ValueError("Arquivo excede o tamanho máximo de 5MB.")
        
        if not file_name:
            raise ValueError("Nome de arquivo inválido.")

        # 2. Validação da Transação (Segurança e Integridade)
        transacao = self.transacao_repo.get_by_id(id_transacao)
        
        if not transacao:
            raise ValueError("Transação não encontrada.")
        
        # Regra de Segurança: Usuário só pode anexar em suas transações
        if transacao.id_usuario != id_usuario:
            raise PermissionError("Usuário não autorizado a acessar esta transação.")
            
        # 3. Salvar no Storage (Camada de Infra)
        # O storage lida com a E/S de disco e retorna o caminho
        caminho_storage = self.storage.save(file_stream, file_name, content_type)
        
        # 4. Criar Entidade de Domínio
        anexo = Anexo(
            id_transacao=id_transacao,
            nome_arquivo=file_name,
            caminho_storage=caminho_storage,
            tipo_mime=content_type,
            tamanho_bytes=content_length
        )
        
        # 5. Salvar metadados no Repositório (Camada de Infra)
        self.anexo_repo.add(anexo)
        
        print(f"Anexo {anexo.id} salvo para transação {id_transacao}.")
        return anexo

class AtualizarTransacao:
    def __init__(self, transacao_repo: ITransacaoRepository):
        self.transacao_repo = transacao_repo

    def execute(self, id_usuario: str, id_transacao: str, 
                dados_atualizados: Dict[str, Any]) -> Transacao:
        
        transacao = self.transacao_repo.get_by_id(id_transacao)
        if not transacao:
            raise ValueError("Transação não encontrada.")
        
        if transacao.id_usuario != id_usuario:
            raise PermissionError("Usuário não autorizado a editar esta transação.")
            
        if transacao.status == StatusTransacao.PROCESSADO:
            raise PermissionError("Não é possível editar uma transação já processada.")

        # Valor e Data NUNCA são atualizados aqui.
        if 'descricao' in dados_atualizados:
            transacao.descricao = dados_atualizados['descricao']
        
        id_categoria = dados_atualizados.get('id_categoria')
        id_perfil = dados_atualizados.get('id_perfil')

        # Atualiza os campos (mesmo que venham nulos/vazios)
        transacao.id_categoria = id_categoria or None
        transacao.id_perfil = id_perfil or None
            
        # Se AMBOS os campos agora tiverem valor, o status muda para PROCESSADO
        if transacao.id_categoria and transacao.id_perfil:
            transacao.status = StatusTransacao.PROCESSADO
            
        self.transacao_repo.update(transacao)
        return transacao
    
class DeletarTransacao:
    def __init__(self, transacao_repo: ITransacaoRepository):
        self.transacao_repo = transacao_repo

    def execute(self, id_usuario: str, id_transacao: str) -> None:
        
        transacao = self.transacao_repo.get_by_id(id_transacao)
        if not transacao:
            print(f"Transação {id_transacao} não encontrada, nada a deletar.")
            return
            
        if transacao.id_usuario != id_usuario:
            raise PermissionError("Usuário não autorizado a deletar esta transação.")
            
        self.transacao_repo.delete(id_transacao)
        print(f"Caso de Uso: Transação {id_transacao} deletada.")
        return

class ListarTransacoesPendentes:
    """
    Caso de Uso: Visualizar Inbox.
    Busca todas as transações do usuário que estão PENDENTES.
    """
    def __init__(self, transacao_repo: ITransacaoRepository):
        self.transacao_repo = transacao_repo

    def execute(self, id_usuario: str) -> List[Transacao]:
        # A lógica de negócio é delegada ao repositório
        transacoes_pendentes = self.transacao_repo.get_pendentes_by_usuario(id_usuario)
        return transacoes_pendentes
    

class CategorizarTransacoesEmLote:
    def __init__(self, transacao_repo: ITransacaoRepository):
        self.transacao_repo = transacao_repo
    def execute(self, id_usuario: str, ids_transacoes: List[str], 
                id_categoria: str, id_perfil: str) -> int:
        if not ids_transacoes:
            raise ValueError("Nenhuma transação selecionada.")
        if not id_categoria or not id_perfil:
            raise ValueError("Categoria e Perfil são obrigatórios.")
        transacoes = self.transacao_repo.get_by_ids(ids_transacoes)
        transacoes_atualizadas = []
        for t in transacoes:
            if t.id_usuario != id_usuario:
                print(f"Aviso: Tentativa de categorizar transação {t.id} de outro usuário.")
                continue
            
            # --- MUDANÇA: Verifica o status antes de categorizar em lote ---
            if t.status == StatusTransacao.PENDENTE:
                t.categorizar(id_categoria=id_categoria, id_perfil=id_perfil)
                transacoes_atualizadas.append(t)
            else:
                print(f"Aviso: Transação {t.id} já processada, ignorando.")

        if transacoes_atualizadas:
            self.transacao_repo.update_batch(transacoes_atualizadas)
        return len(transacoes_atualizadas)
    
class FiltrarTransacoes:
    def __init__(self, transacao_repo: ITransacaoRepository):
        self.transacao_repo = transacao_repo

    def execute(self, id_usuario: str, 
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
        
        if data_de and data_ate and data_ate < data_de:
            raise ValueError("A data 'Até' deve ser maior ou igual à data 'De'.")
        if valor_min is not None and valor_max is not None and valor_max < valor_min:
            raise ValueError("O valor 'Máximo' deve ser maior ou igual ao valor 'Mínimo'.")

        return self.transacao_repo.get_by_filters(
            id_usuario=id_usuario,
            data_de=data_de,
            data_ate=data_ate,
            valor_min=valor_min,
            valor_max=valor_max,
            descricao=descricao,
            status=status,
            id_categoria=id_categoria,
            id_perfil=id_perfil,
            sem_categoria=sem_categoria,
            sem_perfil=sem_perfil
        )

class ObterEstatisticasDashboard:
    """
    Caso de Uso para os cards do Dashboard (Wireframe image_c7f9e7.png).
    Busca Saldo Atual, Receitas (mês) e Despesas (mês).
    """
    def __init__(self, transacao_repo: ITransacaoRepository):
        self.transacao_repo = transacao_repo

    def execute(self, id_usuario: str) -> Dict[str, Any]:
        # Delega a lógica de agregação para o repositório
        return self.transacao_repo.get_dashboard_stats(id_usuario)
