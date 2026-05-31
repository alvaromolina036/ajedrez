from pathlib import Path

from backend.adapters.interfaces.FileAdapter import FileAdapter


class FileAdapterLocal(FileAdapter):
    def __init__(self, base_path: str = "backend/prompts"):
        self.base_path = Path(base_path)

    # Lee un fichero de texto desde la carpeta configurada.
    def read_text_file(self, file_name: str) -> str:
        file_path = self.base_path / file_name
        return file_path.read_text(encoding="utf-8")
