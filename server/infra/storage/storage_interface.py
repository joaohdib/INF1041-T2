from abc import ABC, abstractmethod

class IAnexoStorage(ABC):
    @abstractmethod
    def save(self, file_stream, file_name, mime_type) -> str:
        """ Salva o arquivo e retorna o caminho de storage. """
        pass

    @abstractmethod
    def delete(self, caminho_storage: str) -> None:
        """ Remove o arquivo físico do storage. """
        pass