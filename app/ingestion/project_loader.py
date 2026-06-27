import zipfile
import shutil
from pathlib import Path
from app.config.settings import UPLOAD_DIR
from app.ingestion.file_filter import filter_python_files

class ProjectLoader:
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.project_dir = UPLOAD_DIR / project_id
        self.zip_path = self.project_dir / "source.zip"
        
    def save_and_extract(self, file_content: bytes) -> Path:
        """Save the uploaded zip file to disk and extract it."""
        self.project_dir.mkdir(parents=True, exist_ok=True)
        
        # Save the zip file
        with open(self.zip_path, "wb") as f:
            f.write(file_content)
            
        # Clean up previous extraction if it exists
        extract_dir = self.project_dir / "extracted"
        if extract_dir.exists():
            shutil.rmtree(extract_dir)
            
        # Extract the zip file
        with zipfile.ZipFile(self.zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
            
        return extract_dir

    def scan_python_files(self) -> list[Path]:
        """Scan the extracted directory for Python files."""
        extract_dir = self.project_dir / "extracted"
        if not extract_dir.exists():
            raise ValueError(f"Project {self.project_id} has not been extracted yet.")
            
        return filter_python_files(extract_dir)