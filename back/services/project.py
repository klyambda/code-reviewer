import os
import zipfile
import tempfile
from uuid import uuid4
from datetime import datetime

from services.code import CodeManager
from src.mongo import col_projects, col_files


class ProjectManager:
    def __init__(self, project_id=""):
        self.IGNORED_SYSTEM_DIRECTORIES = {
            ".git",
            "__MACOSX",
            ".idea",
            ".vscode",
            "node_modules",
            "venv",
            ".pytest_cache",
        }
        self.code_manager = CodeManager()
        self.project_id = project_id
        self.structure = []
        self.files_by_folders = {}
        self.file_content_by_name = {}

    def insert_project(self, archive_filename):
        self.project_id = col_projects.insert_one(
            {"name": archive_filename, "created_at": datetime.now()}
        ).inserted_id

    def extract_archive_and_save(self, archive_file):
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                with zipfile.ZipFile(archive_file, "r") as zip_ref:
                    zip_ref.extractall(temp_dir)
                    self.structure = self.build_structure(temp_dir, root_dir=temp_dir)
        except zipfile.BadZipFile:
            raise ValueError("The provided file is not a valid ZIP archive.")
        except Exception as e:
            raise RuntimeError(f"An error occurred while processing the archive: {e}")
        else:
            col_projects.update_one({"_id": self.project_id}, {"$set": {"structure": self.structure}})

    def build_structure(self, path, root_dir=""):
        structure = []
        for item in sorted(os.listdir(path)):
            item_path = os.path.join(path, item)

            # Пропускаем системные папки
            if any(
                item.startswith(ignored)
                for ignored in self.IGNORED_SYSTEM_DIRECTORIES
            ):
                continue

            if os.path.isdir(item_path):
                structure.append({
                    "id": uuid4().hex,
                    "name": item,
                    "type": "folder",
                    "children": self.build_structure(item_path, root_dir)
                })
            else:
                file_id = uuid4().hex
                structure.append(
                    {
                        "id": file_id,
                        "name": item,
                        "type": "file",
                    }
                )
                # сохраняем содержимое файлов
                try:
                    with open(item_path, "r", encoding="utf-8", errors="ignore") as file:
                        content = file.read()
                except Exception:
                    pass
                else:
                    col_files.insert_one({
                        "_id": file_id,
                        "name": item,
                        "content": content,
                        "project_id": self.project_id,
                        "created_at": datetime.now(),
                    })
                    if item.endswith(".py"):
                        definition = self.code_manager.extract_functions_and_classes(content)
                        if item_path not in self.files_by_folders:
                            self.files_by_folders[item_path.lstrip(root_dir)] = []
                        self.files_by_folders[item_path.lstrip(root_dir)].append(definition)
                        self.file_content_by_name[item_path.lstrip(root_dir)] = content

        return structure

    def format_tree(self, structure, prefix=""):
        """
        Преобразует JSON-структуру файловой системы в строку в виде дерева.
        """
        tree_str = ""
        for index, item in enumerate(structure):
            is_last = index == len(structure) - 1  # Проверяем, последний ли это элемент
            branch = "└── " if is_last else "├── "
            next_prefix = "    " if is_last else "│   "

            if item["type"] == "file":
                # Добавляем файл
                tree_str += f"{prefix}{branch}{item['name']}\n"
            elif item["type"] == "folder":
                # Добавляем папку и рекурсивно добавляем ее содержимое
                tree_str += f"{prefix}{branch}{item['name']}\n"
                tree_str += self.format_tree(item["children"], prefix + next_prefix)

        return tree_str
