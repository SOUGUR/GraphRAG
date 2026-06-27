import uuid
import zipfile
from fastapi import APIRouter, UploadFile, File, HTTPException, Path as PathParam
from app.ingestion.project_loader import ProjectLoader
from app.services.ingest_service import IngestService

router = APIRouter()

@router.post("/upload")
async def upload_project(file: UploadFile = File(...)):
    # Validate file extension
    if not file.filename or not file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="Only .zip files are allowed.")
        
    project_id = str(uuid.uuid4())
    loader = ProjectLoader(project_id)
    
    try:
        # Read file content
        file_content = await file.read()
        
        # Save, extract, and scan
        extract_dir = loader.save_and_extract(file_content)
        python_files = loader.scan_python_files()
        
        return {
            "project_id": project_id,
            "status": "success",
            "message": "ZIP extracted and Python files scanned successfully.",
            "python_files_count": len(python_files),
            "sample_files": [str(f.relative_to(extract_dir)) for f in python_files[:5]]
        }
    except zipfile.BadZipFile:
        raise HTTPException(status_code=400, detail="Invalid or corrupted ZIP file.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
    


@router.post("/parse/{project_id}")
async def parse_project(project_id: str = PathParam(...)):
    try:
        service = IngestService(project_id)
        parsed_ir = service.parse_project()
        
        return {
            "project_id": project_id,
            "status": "success",
            "message": "Project parsed into IR successfully.",
            "summary": {
                "files": len(parsed_ir.files),
                "packages": len(parsed_ir.packages),
                "classes": len(parsed_ir.classes),
                "functions": len(parsed_ir.functions),
                "imports": len(parsed_ir.imports)
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing project: {str(e)}")