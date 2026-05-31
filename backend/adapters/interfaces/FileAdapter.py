from abc import ABC, abstractmethod


class FileAdapter(ABC):

    # Lee un fichero de texto.
    @abstractmethod
    def read_text_file(self, file_name: str) -> str:
        pass
