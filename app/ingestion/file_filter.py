from pathlib import Path
from app.config.settings import ALLOWED_EXTENSIONS, IGNORE_DIRS

def is_valid_python_file(file_path: Path) -> bool:
    """Check if the file is a .py file and not inside an ignored directory."""
    if file_path.suffix not in ALLOWED_EXTENSIONS:
        return False
    
    # Ignore files inside virtual environments, caches, etc.
    for part in file_path.parts:
        if part in IGNORE_DIRS:
            return False
            
    return True

def filter_python_files(directory: Path) -> list[Path]:
    """Recursively find all valid Python files in the given directory (deduplicated)."""
    python_files = []
    seen_paths: set[Path] = set()  
    
    for file_path in directory.rglob("*.py"):
        # Resolve to absolute path to handle symlinks/duplicates
        resolved = file_path.resolve()
        if resolved not in seen_paths and is_valid_python_file(file_path):
            python_files.append(file_path)
            seen_paths.add(resolved)
    
    return python_files