from datetime import datetime
from typing import List, Dict, Any
from domain.transacao import Transacao, TipoTransacao, StatusTransacao
from use_cases.repository_interfaces import ITransacaoRepository
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
    # Limites (5MB)
    MAX_SIZE_BYTES = 5 * 1024 * 1024
    ALLOWED_MIMES = ["image/jpeg", "image/png", "application/pdf"]

    def __init__(self, storage: IAnexoStorage, transacao_repo: ITransacaoRepository):
        self.storage = storage
        # Poderíamos usar um IAnexoRepository, mas por simplicidade
        # vamos apenas atualizar a transação. # TODO

    def execute(self, id_transacao: str, file_stream, file_name: str, 
                content_type: str, content_length: int) -> None:
        
        # 1. Validações
        if content_type not in self.ALLOWED_MIMES:
            raise ValueError(f"Formato de arquivo não suportado: {content_type}")
        
        if content_length > self.MAX_SIZE_BYTES:
            raise ValueError("Arquivo excede o tamanho máximo de 5MB.")
            
        # 2. Salvar no Storage
        path = self.storage.save(file_stream, file_name, content_type)
        
        # 3. Associar à Transação
        print(f"Anexo salvo para transação {id_transacao} em {path}")
        pass

class ListarTransacoesPendentes:
    """
    Caso de Uso para PPI-10: Visualizar Inbox.
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
    Caso de Uso para PPI-11: Categorizar em Massa.
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