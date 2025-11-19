import os
import shutil
import uuid

from infra.storage.storage_interface import IAnexoStorage
from werkzeug.utils import secure_filename

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

        :param file_stream: Stream do arquivo (FileStorage ou BytesIO)
        :param file_name: Nome original do arquivo (ex: "recibo.jpg")
        :param mime_type: Tipo MIME (ex: "image/jpeg")
        :return: Caminho relativo salvo (ex: "uploads/uuid-aleatorio.jpg")
        """
        # 1. Obter a extensão do arquivo original
        ext = ""
        if "." in file_name:
            ext = file_name.rsplit(".", 1)[1].lower()

        # 2. Gerar um nome de arquivo seguro e único
        secure_name = str(uuid.uuid4()) + "." + secure_filename(ext)

        # 3. Definir o caminho completo de salvamento
        save_path = os.path.join(UPLOADS_FOLDER, secure_name)

        try:
            # 4. Salvar o stream do arquivo no caminho (Compatível com BytesIO e FileStorage)
            with open(save_path, "wb") as f:
                if hasattr(file_stream, "save"):
                    file_stream.seek(0)
                    shutil.copyfileobj(file_stream, f)
                else:
                    file_stream.seek(0)
                    f.write(file_stream.read())

            # 5. Retornar o caminho *relativo* para ser salvo no banco
            return save_path

        except Exception as e:
            print(f"Erro ao salvar arquivo no storage local: {e}")
            if os.path.exists(save_path):
                os.remove(save_path)
            raise IOError(f"Não foi possível salvar o arquivo: {file_name}")

    def delete(self, caminho_storage: str) -> None:
        """Remove o arquivo físico se ele existir."""
        try:
            if os.path.exists(caminho_storage):
                os.remove(caminho_storage)
                print(f"Arquivo removido do storage: {caminho_storage}")
            else:
                print(f"Arquivo não encontrado para remoção: {caminho_storage}")
        except Exception as e:
            print(f"Erro ao deletar arquivo do storage: {e}")
