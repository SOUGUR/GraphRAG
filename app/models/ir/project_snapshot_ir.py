from pydantic import Field, BaseModel
from app.models.ir.project_ir import ProjectIR
from app.models.ir.package_ir import PackageIR
from app.models.ir.file_ir import FileIR
from app.models.ir.import_ir import ImportIR
from app.models.ir.class_ir import ClassIR
from app.models.ir.function_ir import FunctionIR
from app.models.ir.variable_ir import VariableIR
from app.models.ir.dependency_ir import DependencyIR

class ParsedProjectIR(BaseModel):
    project: ProjectIR
    packages: list[PackageIR] = Field(default_factory=list)
    files: list[FileIR] = Field(default_factory=list)
    imports: list[ImportIR] = Field(default_factory=list)
    classes: list[ClassIR] = Field(default_factory=list)
    functions: list[FunctionIR] = Field(default_factory=list)
    variables: list[VariableIR] = Field(default_factory=list)
    dependencies: list[DependencyIR] = Field(default_factory=list)