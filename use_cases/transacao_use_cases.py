from datetime import datetime
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