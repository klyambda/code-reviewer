import ast
import sys
import importlib.util
from pathlib import Path


class CodeManager:
    def extract_functions_and_classes(self, source_code):
        tree = ast.parse(source_code)
        functions_and_methods = []

        def extract(node):
            if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                res = parse_import_node(node)
                if res:
                    functions_and_methods.append(res)
            elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                functions_and_methods.append(parse_function_node(node))
            elif isinstance(node, ast.ClassDef):
                functions_and_methods.append(parse_class_node(node))
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) or isinstance(item, ast.AsyncFunctionDef):
                        functions_and_methods.append(parse_function_node(item))

        def parse_import_node(node):
            imports = []
            if isinstance(node, ast.Import):
                for name in node.names:
                    if self.is_standard_or_installed(name.name.split(".")[0]):
                        imports.append(name.name)
            elif isinstance(node, ast.ImportFrom):
                for name in node.names:
                    if self.is_standard_or_installed(node.module):
                        imports.append(f"{node.module}.{name.name}")

            res = ""
            for imp in imports:
                res += f"import {imp}\n"

            return res.strip("\n")

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
                bases = []
                for base in node.bases:
                    if isinstance(base, ast.Attribute):
                        bases.append(base.value.id)
                    elif isinstance(base, ast.Name):
                        bases.append(base.id)
                result += f"({', '.join(bases)})"

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
                if decorator_name:
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
                result += f" -> {ast.unparse(node.returns)}"

            # докстринг
            docstring = ast.get_docstring(node)
            if docstring:
                result += f'\n"""{docstring}"""'

            return result

        # Рекурсивно обрабатываем дерево
        for node in tree.body:
            try:
                extract(node)
            except Exception:
                pass

        return "\n".join(functions_and_methods)

    def is_standard_or_installed(self, module_name):
        """
        Проверяет, является ли модуль встроенным в Python или установленным через pip.
        """
        try:
            # Попытка найти спецификацию модуля
            spec = importlib.util.find_spec(module_name)
            if spec is None or spec.origin is None:
                return False

            # Проверяем, находится ли модуль в стандартной библиотеке или site-packages
            origin_path = Path(spec.origin)
            if "site-packages" in origin_path.parts or "dist-packages" in origin_path.parts:
                return True
            if sys.base_prefix in spec.origin:
                return True
            return False
        except ModuleNotFoundError:
            return False
