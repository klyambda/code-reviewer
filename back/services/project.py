import os
import zipfile
import tempfile
from uuid import uuid4
from datetime import datetime

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

    def extract_archive_and_save(self, archive_file, project_id):
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                with zipfile.ZipFile(archive_file, "r") as zip_ref:
                    zip_ref.extractall(temp_dir)
                    structure = self.build_structure(temp_dir, project_id)
        except zipfile.BadZipFile:
            raise ValueError("The provided file is not a valid ZIP archive.")
        except Exception as e:
            raise RuntimeError(f"An error occurred while processing the archive: {e}")
        else:
            col_projects.update_one({"_id": project_id}, {"$set": {"structure": structure}})

    def build_structure(self, path, project_id):
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
                    "children": self.build_structure(item_path, project_id)
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
                # сохраняем содержимое python файлов
                if item.endswith(".py"):
                    with open(item_path, "r", encoding="utf-8", errors="ignore") as file:
                        content = file.read()
                    col_files.insert_one(
                        {
                            "_id": file_id,
                            "name": item,
                            "content": content,
                            "project_id": project_id,
                            "created_at": datetime.now(),
                        }
                    )
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
