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
    def extract_functions_and_classes(self, source_code):
        tree = ast.parse(source_code)
        functions_and_methods = []

        def extract(node):
            if isinstance(node, ast.FunctionDef):
                functions_and_methods.append(parse_function_node(node))
            elif isinstance(node, ast.AsyncFunctionDef):
                functions_and_methods.append(parse_function_node(node))
            elif isinstance(node, ast.ClassDef):
                functions_and_methods.append(parse_class_node(node))
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):  # Методы в классах
                        functions_and_methods.append(parse_function_node(item))

        def parse_class_node(node):
            result = ""

            # декораторы
            for decorator in node.decorator_list:
                decorator_name = ast.unparse(decorator).strip()
                result += f"@{decorator_name}\n"

            # имя
            result += f"class {node.name}"

            # наследуеммые классы
            if node.bases:
                result += f"({', '.join([base.id for base in node.bases])}):"
            else:
                result += ":"

            # докстринг
            docstring = ast.get_docstring(node)
            if docstring:
                result += f'\n"""{docstring}"""'

            return result

        def parse_function_node(node):
            result = ""

            # декораторы
            for decorator in node.decorator_list:
                decorator_name = ast.unparse(decorator).strip()
                result += f"@{decorator_name}\n"

            # имя
            definition = f"def {node.name}"
            if isinstance(node, ast.AsyncFunctionDef):
                definition = f"async {definition}"
            result += definition

            # параметры
            params = {}
            for arg in node.args.args:
                annotation = ast.unparse(arg.annotation) if arg.annotation else None
                params[arg.arg] = {"default": None, "annotation": annotation}

            defaults = node.args.defaults
            default_offset = len(node.args.args) - len(defaults)
            for i, default in enumerate(defaults):
                param_name = node.args.args[default_offset + i].arg
                params[param_name]["default"] = ast.unparse(default)

            if node.args.vararg:
                annotation = ast.unparse(node.args.vararg.annotation) if node.args.vararg.annotation else None
                params[f"*{node.args.vararg.arg}"] = {"default": None, "annotation": annotation}

            if node.args.kwarg:
                annotation = ast.unparse(node.args.kwarg.annotation) if node.args.kwarg.annotation else None
                params[f"**{node.args.kwarg.arg}"] = {"default": None, "annotation": annotation}

            function_args = []
            for k, v in params.items():
                arg = k
                if v["annotation"]:
                    arg = f"{arg}: {v['annotation']}"
                if v["default"]:
                    arg = f"{arg} = {v['default']}"
                function_args.append(arg)
            result += f"({', '.join(function_args)})"

            # тип возврата
            if node.returns:
                result += f" -> {ast.unparse(node.returns)}:"
            else:
                result += ":"

            # докстринг
            docstring = ast.get_docstring(node)
            if docstring:
                result += f'\n"""{docstring}"""'

            return result

        # Рекурсивно обрабатываем дерево
        for node in tree.body:
            extract(node)

        return functions_and_methods
