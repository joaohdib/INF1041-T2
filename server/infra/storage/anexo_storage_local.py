import os
import uuid
from werkzeug.utils import secure_filename
from infra.storage.storage_interface import IAnexoStorage

# Define a pasta onde os uploads ficarão
UPLOADS_FOLDER = "uploads"

class AnexoStorageLocal(IAnexoStorage):
    """
    Implementação concreta do Storage que salva arquivos 
    localmente em uma pasta 'uploads'.
    """
    def __init__(self):
        # Garante que a pasta de uploads existentes 
        try:
            if not os.path.exists(UPLOADS_FOLDER):
                os.makedirs(UPLOADS_FOLDER)
                print(f"Pasta de uploads criada em: {UPLOADS_FOLDER}")
        except OSError as e:
            print(f"Erro ao criar pasta de uploads: {e}")
            raise

    def save(self, file_stream, file_name: str, mime_type: str) -> str:
        """
        Salva o arquivo fisicamente no disco e retorna o caminho relativo.
        
        :param file_stream: Objeto FileStorage do Flask (request.files['anexo'])
        :param file_name: Nome original do arquivo (ex: "recibo.jpg")
        :param mime_type: Tipo MIME (ex: "image/jpeg")
        :return: Caminho relativo salvo (ex: "uploads/uuid-aleatorio.jpg")
        """
        # 1. Obter a extensão do arquivo original
        ext = ""
        if '.' in file_name:
            ext = file_name.rsplit('.', 1)[1].lower()
        
        # 2. Gerar um nome de arquivo seguro e único
        secure_name = str(uuid.uuid4()) + "." + secure_filename(ext)
        
        # 3. Definir o caminho completo de salvamento
        save_path = os.path.join(UPLOADS_FOLDER, secure_name)
        
        try:
            # 4. Salvar o stream do arquivo no caminho
            file_stream.save(save_path)
            
            # 5. Retornar o caminho *relativo* para ser salvo no banco
            return save_path
        
        except Exception as e:
            print(f"Erro ao salvar arquivo no storage local: {e}")
            # Lança um erro genérico de I/O
            raise IOError(f"Não foi possível salvar o arquivo: {file_name}")