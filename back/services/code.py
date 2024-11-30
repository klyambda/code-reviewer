import ast
import astor


class FunctionExtractor(ast.NodeVisitor):
    def __init__(self):
        self.functions = []

    def visit_FunctionDef(self, node):
        self._process_function(node)

    def visit_AsyncFunctionDef(self, node):
        self._process_function(node)

    def _process_function(self, node):
        # игнорируем вложенные функции
        if isinstance(node.parent, ast.Module):
            source_code = astor.to_source(node)
            self.functions.append(source_code)
            return astor.to_source(node)


class CodeManager:
    def extract_functions(self, source_code):
        """
        Разделяет код на отдельные функции
        """
        tree = ast.parse(source_code)

        # добавляем ссылки на родительские узлы (для определения уровня вложенности).
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                child.parent = node

        extractor = FunctionExtractor()
        extractor.visit(tree)

        return extractor.functions
