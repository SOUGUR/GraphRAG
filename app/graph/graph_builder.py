from app.graph.neo4j_manager import neo4j_manager
from app.models.ir.project_snapshot_ir import ParsedProjectIR

class GraphBuilder:
    def __init__(self, parsed_project: ParsedProjectIR):
        self.ir = parsed_project
        self.project_id = parsed_project.project.id

    def build(self):
        self._create_nodes()
        self._create_edges()

    def _get_node_properties(self, node, extra_props: dict = None) -> dict:
        """
        Extract only primitive properties from a Pydantic model.
        - exclude_none=True removes None values (NO_VALUE in Neo4j)
        - exclude nested objects/lists that should be separate nodes
        """
        # Fields to exclude because they are nested objects or lists of objects
        exclude_fields = {
            'methods', 'variables', 'parameters', 'decorators', 
            'calls', 'returns', 'docstring', 'bases'
        }
        
        props = node.model_dump(exclude_none=True, exclude=exclude_fields)
        
        if extra_props:
            props.update(extra_props)
            
        return props

    def _run_unwind(self, label: str, id_prop: str, nodes: list[dict]):
        if not nodes: 
            return
        
        query = f"""
        UNWIND $nodes AS node
        MERGE (n:{label} {{ {id_prop}: node.{id_prop} }})
        SET n += node
        """
        neo4j_manager.execute_query(query, {"nodes": nodes})

    def _run_unwind_edge(self, source_label: str, target_label: str, rel_type: str, edges: list[dict]):
        if not edges: 
            return
        query = f"""
        UNWIND $edges AS edge
        MATCH (s:{source_label} {{id: edge.source_id}})
        MATCH (t:{target_label} {{id: edge.target_id}})
        MERGE (s)-[r:{rel_type}]->(t)
        """
        neo4j_manager.execute_query(query, {"edges": edges})

    def _create_nodes(self):
        # 1. Project
        self._run_unwind("Project", "id", [
            self._get_node_properties(self.ir.project, {"project_id": self.project_id})
        ])

        # 2. Packages
        self._run_unwind("Package", "id", [
            self._get_node_properties(pkg, {"project_id": self.project_id}) 
            for pkg in self.ir.packages
        ])

        # 3. Files
        self._run_unwind("File", "id", [
            self._get_node_properties(f, {"project_id": self.project_id}) 
            for f in self.ir.files
        ])

        # 4. Classes
        self._run_unwind("Class", "id", [
            self._get_node_properties(c, {"project_id": self.project_id}) 
            for c in self.ir.classes
        ])

        # 5. Functions (Module level + Methods)
        funcs_data = [
            self._get_node_properties(f, {"project_id": self.project_id}) 
            for f in self.ir.functions
        ]
        for c in self.ir.classes:
            for m in c.methods:
                funcs_data.append(self._get_node_properties(m, {"project_id": self.project_id}))
        self._run_unwind("Function", "id", funcs_data)

        # 6. Variables (Module level + Class variables)
        vars_data = [
            self._get_node_properties(v, {"project_id": self.project_id}) 
            for v in self.ir.variables
        ]
        for c in self.ir.classes:
            for v in c.variables:
                vars_data.append(self._get_node_properties(v, {"project_id": self.project_id}))
        self._run_unwind("Variable", "id", vars_data)

        # 7. Parameters
        params_data = []
        for f in self.ir.functions:
            for p in f.parameters:
                params_data.append(self._get_node_properties(p, {
                    "project_id": self.project_id, 
                    "function_id": f.id
                }))
        for c in self.ir.classes:
            for m in c.methods:
                for p in m.parameters:
                    params_data.append(self._get_node_properties(p, {
                        "project_id": self.project_id, 
                        "function_id": m.id
                    }))
        self._run_unwind("Parameter", "id", params_data)

    def _create_edges(self):
        # Project -> Package
        self._run_unwind_edge("Project", "Package", "CONTAINS", [
            {"source_id": self.project_id, "target_id": pkg.id} 
            for pkg in self.ir.packages
        ])

        # Package -> File
        pkg_edges = []
        for f in self.ir.files:
            best_match = max(
                (pkg for pkg in self.ir.packages if f.path.startswith(pkg.path) or pkg.path == "."), 
                key=lambda p: len(p.path), 
                default=None
            )
            if best_match:
                pkg_edges.append({"source_id": best_match.id, "target_id": f.id})
        self._run_unwind_edge("Package", "File", "CONTAINS", pkg_edges)

        # File -> Class / Function / Variable
        self._run_unwind_edge("File", "Class", "DEFINES", [
            {"source_id": c.file_id, "target_id": c.id} 
            for c in self.ir.classes if c.file_id
        ])
        self._run_unwind_edge("File", "Function", "DEFINES", [
            {"source_id": f.file_id, "target_id": f.id} 
            for f in self.ir.functions if f.file_id and not f.parent_id
        ])
        self._run_unwind_edge("File", "Variable", "DEFINES", [
            {"source_id": v.file_id, "target_id": v.id} 
            for v in self.ir.variables if v.file_id and not v.parent_id
        ])

        # Class -> Method / Class Variable
        class_method_edges = [
            {"source_id": c.id, "target_id": m.id} 
            for c in self.ir.classes for m in c.methods
        ]
        self._run_unwind_edge("Class", "Function", "DEFINES", class_method_edges)
        
        class_var_edges = [
            {"source_id": c.id, "target_id": v.id} 
            for c in self.ir.classes for v in c.variables
        ]
        self._run_unwind_edge("Class", "Variable", "DEFINES", class_var_edges)

        # Function -> Parameter
        param_edges = [
            {"source_id": f.id, "target_id": p.id} 
            for f in self.ir.functions for p in f.parameters
        ]
        for c in self.ir.classes:
            for m in c.methods:
                for p in m.parameters:
                    param_edges.append({"source_id": m.id, "target_id": p.id})
        self._run_unwind_edge("Function", "Parameter", "HAS_PARAMETER", param_edges)

        # Inheritance & Calls (Targets might be external, so we MERGE them)
        self._run_dynamic_edges("INHERITS", "Class", "bases")
        self._run_dynamic_edges("CALLS", "Function", "calls")

    def _run_dynamic_edges(self, rel_type: str, target_label: str, attr_name: str):
        edges = []
        # Module functions
        for f in self.ir.functions:
            for item in getattr(f, attr_name, []):
                target_name = item if isinstance(item, str) else getattr(item, 'callee', getattr(item, 'name', ''))
                edges.append({
                    "source_id": f.id, 
                    "target_name": target_name, 
                    "lineno": getattr(item, 'lineno', 0)
                })
        # Class methods
        for c in self.ir.classes:
            for m in c.methods:
                for item in getattr(m, attr_name, []):
                    target_name = item if isinstance(item, str) else getattr(item, 'callee', getattr(item, 'name', ''))
                    edges.append({
                        "source_id": m.id, 
                        "target_name": target_name, 
                        "lineno": getattr(item, 'lineno', 0)
                    })
                    
        if not edges: 
            return
        
        query = f"""
        UNWIND $edges AS edge
        MATCH (s:Function {{id: edge.source_id}})
        MERGE (t:{target_label} {{name: edge.target_name, project_id: $project_id}})
        MERGE (s)-[r:{rel_type} {{lineno: edge.lineno}}]->(t)
        """
        # Special case for INHERITS where source is Class
        if rel_type == "INHERITS":
            query = query.replace("MATCH (s:Function", "MATCH (s:Class")
            
        neo4j_manager.execute_query(query, {"edges": edges, "project_id": self.project_id})