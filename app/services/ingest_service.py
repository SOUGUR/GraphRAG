
from app.config.settings import UPLOAD_DIR
from app.ingestion.project_loader import ProjectLoader
from app.parser.ast_parser import parse_file
from app.models.ir.project_ir import ProjectIR
from app.models.ir.package_ir import PackageIR
from app.models.ir.project_snapshot_ir import ParsedProjectIR

class IngestService:
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.loader = ProjectLoader(project_id)
        
    def parse_project(self) -> ParsedProjectIR:
        python_files = self.loader.scan_python_files()
        extract_dir = self.loader.project_dir / "extracted"
        
        project_ir = ProjectIR(name=self.project_id, root_path=str(extract_dir.relative_to(UPLOAD_DIR)))
        parsed_project = ParsedProjectIR(project=project_ir)
        packages_seen = set()
        
        for file_path in python_files:
            file_ir, imports, classes, functions, variables = parse_file(file_path, extract_dir)
            
            for cls in classes: 
                cls.file_id = file_ir.id
            for func in functions: 
                func.file_id = file_ir.id
            for var in variables: 
                var.file_id = file_ir.id
            
            for cls in classes:
                for method in cls.methods:
                    method.file_id = file_ir.id
                    method.parent_id = cls.id
                for var in cls.variables:
                    var.file_id = file_ir.id
                    var.parent_id = cls.id
            # -----------------------------------------
            
            parsed_project.files.append(file_ir)
            parsed_project.imports.extend(imports)
            parsed_project.classes.extend(classes)
            parsed_project.functions.extend(functions)
            parsed_project.variables.extend(variables)
            
            package_path = file_path.parent.relative_to(extract_dir)
            package_name = str(package_path).replace("/", ".").replace("\\", ".") or "root"
                
            if package_name not in packages_seen:
                packages_seen.add(package_name)
                parsed_project.packages.append(PackageIR(name=package_name, path=str(package_path)))
                
        return parsed_project