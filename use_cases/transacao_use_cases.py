from datetime import datetime
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
                data: datetime | None = None, descricao: str | None = None) -> Transacao:
        
        # 1. Validação de regras de negócio
        if valor <= 0:
            raise ValueError("O valor deve ser maior que zero.")
            
        # 2. Criação da entidade
        transacao = Transacao(
            id_usuario=id_usuario,
            valor=valor,
            tipo=TipoTransacao(tipo.upper()),
            data=data or datetime.now(),
            descricao=descricao,
            status=StatusTransacao.PENDENTE # Novas transações vão para a Inbox
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
    """
    Caso de Uso: Categorizar em Massa.
    Aplica categoria e perfil em múltiplas transações de uma vez.
    """
    def __init__(self, transacao_repo: ITransacaoRepository):
        self.transacao_repo = transacao_repo

    def execute(self, id_usuario: str, ids_transacoes: List[str], 
                id_categoria: str, id_perfil: str) -> int:
        
        # 1. Validação de entrada
        if not ids_transacoes:
            raise ValueError("Nenhuma transação selecionada.")
        if not id_categoria or not id_perfil:
            raise ValueError("Categoria e Perfil são obrigatórios.")

        # 2. Busca as transações
        transacoes = self.transacao_repo.get_by_ids(ids_transacoes)
        
        transacoes_atualizadas = []
        
        # 3. Aplica a regra de negócio (Camada de Domínio)
        for t in transacoes:
            # Regra de segurança: garante que o usuário só pode categorizar
            # transações que pertencem a ele.
            if t.id_usuario != id_usuario:
                print(f"Aviso: Tentativa de categorizar transação {t.id} de outro usuário.")
                continue
            
            # Utiliza o método da própria entidade de domínio
            t.categorizar(id_categoria=id_categoria, id_perfil=id_perfil)
            transacoes_atualizadas.append(t)

        # 4. Persiste em lote
        if transacoes_atualizadas:
            self.transacao_repo.update_batch(transacoes_atualizadas)
            
        # 5. Retorna o número de transações atualizadas com sucesso
        return len(transacoes_atualizadas)
    

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