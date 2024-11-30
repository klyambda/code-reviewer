import zipfile
import tempfile
from datetime import datetime

from loguru import logger

from src.mongo import col_projects, col_files


class ProjectManager:
    def __init__(self):
        self.IGNORED_SYSTEM_DIRECTORIES = {
            ".git",
            "__MACOSX",
            ".idea",
            ".vscode",
            "node_modules",
            "venv",
            ".pytest_cache",
        }

    def insert_project(self, archive_filename):
        project_id = col_projects.insert_one(
            {"name": archive_filename, "created_at": datetime.now()}
        ).inserted_id
        return project_id

    def extract_archive_and_return_result(self, archive_file, project_id):
        result = {
            "structure": {},
            "files": [],
        }
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                result["structure"], result["files"] = self._get_tree_and_files(archive_file, temp_dir, project_id)
        except zipfile.BadZipFile:
            raise ValueError("The provided file is not a valid ZIP archive.")
        except Exception as e:
            raise RuntimeError(f"An error occurred while processing the archive: {e}")

        return result

    def _get_tree_and_files(self, archive_file, temp_dir, project_id):
        tree = {}
        files = []

        with zipfile.ZipFile(archive_file, "r") as zip_ref:
            zip_ref.extractall(temp_dir)
            for file in zip_ref.namelist():
                parts = file.split("/")
                current_level = tree

                skip = False
                for part in parts:
                    # Проверка на игнорируемую папку
                    if part in self.IGNORED_SYSTEM_DIRECTORIES:
                        skip = True
                        break

                if skip:
                    continue

                for part in parts:
                    # Пропустить пустые части (например, из-за `/` в конце)
                    if part == "":
                        continue
                    if part not in current_level:
                        # Это файл
                        if part == parts[-1] and not file.endswith("/"):
                            current_level[part] = None

                            # сохраняем только .py файлы
                            if not file.endswith(".py"):
                                continue

                            # проверка, что путь не попадает в игнорируемую папку
                            if any(
                                file.startswith(ignored)
                                for ignored in self.IGNORED_SYSTEM_DIRECTORIES
                            ):
                                continue

                            try:
                                files.append(
                                    {
                                        "path": part,
                                        "filename": file,
                                        "content": zip_ref.read(file).decode("utf-8"),
                                        "project_id": project_id,
                                        "created_at": datetime.now(),
                                    }
                                )
                            except UnicodeDecodeError:
                                # Пропускаем файлы, которые не удается декодировать как текст
                                logger.exception(
                                    f"Не удалось декодировать {file} как текст."
                                )
                        else:
                            # Это директория
                            current_level[part] = {}
                    current_level = current_level[part]

        col_files.insert_many(files)
        col_projects.update_one({"_id": project_id}, {"$set": {"structure": tree}})

        return tree, files

    def format_tree(self, tree, indent=""):
        """
        Форматирует дерево каталогов из словаря в строку.
        """
        result = []
        entries = list(tree.keys())

        for i, entry in enumerate(entries):
            is_last = i == len(entries) - 1
            connector = "└── " if is_last else "├── "

            # Добавляем текущий элемент
            result.append(f"{indent}{connector}{entry}")

            # Если это папка с содержимым, рекурсивно добавляем её содержимое
            if isinstance(tree[entry], dict):
                deeper_indent = indent + ("    " if is_last else "│   ")
                result.append(self.format_tree(tree[entry], deeper_indent))

        return "\n".join(result)
