"""
Python Script Runner Module
Handles script execution, collection management, and storage
"""

import os
import json
import io
import sys
import time
import traceback
import shutil
import multiprocessing
import builtins
from typing import List, Dict, Any, Optional
from datetime import datetime
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path


# Module-level safe_import function for multiprocessing compatibility
def safe_import(name, globals=None, locals=None, fromlist=(), level=0):
    """Restricted import function that blocks dangerous modules"""
    blocked_modules = ['os', 'sys', 'subprocess', 'shutil', 'builtins', 'pathlib', 'importlib']
    if name in blocked_modules or (fromlist and any(m in blocked_modules for m in fromlist)):
        raise ImportError(f"Import of '{name}' is not allowed for security reasons")
    return __import__(name, globals, locals, fromlist, level)


class CollectionManager:
    """Manages script collections and file storage"""

    def __init__(self, base_path: str = "./scripts"):
        self.base_path = Path(base_path)
        self.collections_file = self.base_path / "collections.json"
        self._ensure_base_structure()

    def _ensure_base_structure(self):
        """Ensure base directory and collections file exist"""
        self.base_path.mkdir(exist_ok=True)
        if not self.collections_file.exists():
            self._save_collections({
                "collections": {
                    "Uncategorized": {
                        "created": datetime.now().isoformat(),
                        "scripts": []
                    }
                }
            })

        # Ensure Uncategorized directory exists
        (self.base_path / "Uncategorized").mkdir(exist_ok=True)

    def _load_collections(self) -> Dict[str, Any]:
        """Load collections metadata"""
        try:
            with open(self.collections_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {"collections": {"Uncategorized": {"created": datetime.now().isoformat(), "scripts": []}}}

    def _save_collections(self, data: Dict[str, Any]):
        """Save collections metadata"""
        with open(self.collections_file, 'w') as f:
            json.dump(data, f, indent=2)

    def create_collection(self, name: str) -> bool:
        """Create a new collection"""
        data = self._load_collections()
        if name in data["collections"]:
            return False

        data["collections"][name] = {
            "created": datetime.now().isoformat(),
            "scripts": []
        }

        # Create directory
        (self.base_path / name).mkdir(exist_ok=True)

        self._save_collections(data)
        return True

    def delete_collection(self, name: str) -> bool:
        """Delete a collection and its scripts"""
        if name == "Uncategorized":
            return False  # Cannot delete default collection

        data = self._load_collections()
        if name not in data["collections"]:
            return False

        del data["collections"][name]
        self._save_collections(data)

        # Delete directory
        dir_path = self.base_path / name
        if dir_path.exists():
            shutil.rmtree(dir_path)

        return True

    def list_collections(self) -> List[str]:
        """List all collection names"""
        data = self._load_collections()
        return list(data["collections"].keys())

    def get_scripts_in_collection(self, collection: str) -> List[Dict[str, Any]]:
        """Get list of scripts in a collection"""
        data = self._load_collections()
        return data["collections"].get(collection, {}).get("scripts", [])

    def add_script_to_collection(self, collection: str, script_metadata: Dict[str, Any]):
        """Add script metadata to a collection"""
        data = self._load_collections()
        if collection not in data["collections"]:
            return # Should probably raise or return False

        # Remove existing if present (update)
        scripts = data["collections"][collection]["scripts"]
        scripts = [s for s in scripts if s["name"] != script_metadata["name"]]
        scripts.append(script_metadata)
        data["collections"][collection]["scripts"] = scripts

        self._save_collections(data)

    def remove_script_from_collection(self, collection: str, script_name: str):
        """Remove script metadata from a collection"""
        data = self._load_collections()
        if collection in data["collections"]:
            scripts = data["collections"][collection]["scripts"]
            scripts = [s for s in scripts if s["name"] != script_name]
            data["collections"][collection]["scripts"] = scripts
            self._save_collections(data)


def _worker_process(code: str, input_str: str, return_dict: Dict, safe_globals: Dict):
    """
    Worker process for executing script securely.
    """
    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()

    # Mock input() to return values from input_str
    input_iter = iter(input_str.splitlines())
    def mock_input(prompt=None):
        if prompt:
             print(prompt, end='', file=stdout_capture)
        try:
            val = next(input_iter)
            # Echo input to stdout like a real terminal
            print(val, file=stdout_capture)
            return val
        except StopIteration:
             raise EOFError("EOF when reading a line")

    safe_globals['__builtins__']['input'] = mock_input

    # Override print to capture output
    # builtins.print points to the real print, but we need to redirect it in this process
    # Since we are using redirect_stdout, standard print works fine.

    try:
        with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
            local_scope = {}
            exec(code, safe_globals, local_scope)

            if 'main' in local_scope and callable(local_scope['main']):
                # If main accepts arguments, we could pass them, but for now no args
                 return_dict['result'] = local_scope['main']()
            else:
                 return_dict['result'] = None

        return_dict['success'] = True
        return_dict['stdout'] = stdout_capture.getvalue()
        return_dict['stderr'] = stderr_capture.getvalue()

    except Exception as e:
        return_dict['success'] = False
        return_dict['error'] = str(e)
        return_dict['stdout'] = stdout_capture.getvalue()

        # Capture full traceback
        tb_io = io.StringIO()
        traceback.print_exc(file=tb_io)
        return_dict['stderr'] = stderr_capture.getvalue() + tb_io.getvalue()


class ScriptExecutor:
    """Handles safe script execution with timeout and capture"""

    def execute(self, code: str, input_str: str = "", timeout: int = 30) -> Dict[str, Any]:
        """
        Execute python code and capture output using multiprocessing for isolation and timeout.
        """
        start_time = time.time()

        manager = multiprocessing.Manager()
        return_dict = manager.dict()

        # Restricted globals - using module-level safe_import
        safe_globals = {
            '__builtins__': {
                'print': print,
                'len': len,
                'range': range,
                'str': str,
                'int': int,
                'float': float,
                'list': list,
                'dict': dict,
                'set': set,
                'tuple': tuple,
                'bool': bool,
                'True': True,
                'False': False,
                'None': None,
                'abs': abs,
                'all': all,
                'any': any,
                'enumerate': enumerate,
                'filter': filter,
                'isinstance': isinstance,
                'map': map,
                'max': max,
                'min': min,
                'round': round,
                'sorted': sorted,
                'sum': sum,
                'zip': zip,
                '__import__': safe_import,
                'Exception': Exception,
                'ValueError': ValueError,
                'TypeError': TypeError,
                'IndexError': IndexError,
                'KeyError': KeyError,
                'AttributeError': AttributeError,
                'NameError': NameError,
                'ImportError': ImportError,
                'RuntimeError': RuntimeError,
            }
        }

        p = multiprocessing.Process(
            target=_worker_process,
            args=(code, input_str, return_dict, safe_globals)
        )

        p.start()
        p.join(timeout)

        execution_time = time.time() - start_time

        if p.is_alive():
            p.terminate()
            p.join()
            return {
                "success": False,
                "stdout": return_dict.get('stdout', ''),
                "stderr": return_dict.get('stderr', '') + "\nTimeout exceeded",
                "result": None,
                "execution_time": timeout,
                "error": "Timeout exceeded"
            }

        if not return_dict.get('success', False):
             return {
                "success": False,
                "stdout": return_dict.get('stdout', ''),
                "stderr": return_dict.get('stderr', ''),
                "result": None,
                "execution_time": execution_time,
                "error": return_dict.get('error', 'Unknown error')
            }

        return {
            "success": True,
            "stdout": return_dict.get('stdout', ''),
            "stderr": return_dict.get('stderr', ''),
            "result": return_dict.get('result'),
            "execution_time": execution_time,
            "error": None
        }


class ScriptRunner:
    """Main interface for script management"""

    def __init__(self, base_path: str = "./scripts"):
        self.collection_manager = CollectionManager(base_path)
        self.executor = ScriptExecutor()
        self.base_path = Path(base_path)

    def save_script(self, name: str, code: str, collection: str, description: str = "", tags: List[str] = None) -> bool:
        """Save a script to a collection"""
        if tags is None:
            tags = []

        # Ensure collection exists
        if collection not in self.collection_manager.list_collections():
            return False

        # Sanitize name to prevent path traversal
        clean_name = "".join(c for c in name if c.isalnum() or c in ('-', '_')).strip()
        if not clean_name:
            return False

        filename = f"{clean_name}.py"
        file_path = self.base_path / collection / filename

        # Write code to file
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(code)
        except IOError:
            return False

        # Update metadata
        metadata = {
            "name": name,
            "filename": filename,
            "description": description,
            "tags": tags,
            "created": datetime.now().isoformat(), # Ideally preserve creation time if exists
            "modified": datetime.now().isoformat()
        }

        # Check if updating existing to preserve creation time
        existing_scripts = self.collection_manager.get_scripts_in_collection(collection)
        for s in existing_scripts:
            if s["name"] == name:
                metadata["created"] = s.get("created", metadata["created"])
                break

        self.collection_manager.add_script_to_collection(collection, metadata)
        return True

    def load_script(self, name: str, collection: str) -> Dict[str, Any]:
        """Load script code and metadata"""
        scripts = self.collection_manager.get_scripts_in_collection(collection)
        metadata = next((s for s in scripts if s["name"] == name), None)

        if not metadata:
            return None

        file_path = self.base_path / collection / metadata["filename"]
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
        except FileNotFoundError:
            return None

        return {
            "code": code,
            "metadata": metadata
        }

    def delete_script(self, name: str, collection: str) -> bool:
        """Delete a script"""
        scripts = self.collection_manager.get_scripts_in_collection(collection)
        metadata = next((s for s in scripts if s["name"] == name), None)

        if not metadata:
            return False

        file_path = self.base_path / collection / metadata["filename"]
        if file_path.exists():
            os.remove(file_path)

        self.collection_manager.remove_script_from_collection(collection, name)
        return True

    def list_all_scripts(self) -> List[Dict[str, Any]]:
        """List all scripts across all collections"""
        all_scripts = []
        for col in self.collection_manager.list_collections():
            scripts = self.collection_manager.get_scripts_in_collection(col)
            for s in scripts:
                s_copy = s.copy()
                s_copy["collection"] = col
                all_scripts.append(s_copy)
        return all_scripts

    def search_scripts(self, query: str) -> List[Dict[str, Any]]:
        """Search scripts by name or tags"""
        query = query.lower()
        results = []
        for script in self.list_all_scripts():
            name_match = query in script["name"].lower()
            tag_match = any(query in tag.lower() for tag in script.get("tags", []))
            if name_match or tag_match:
                results.append(script)
        return results

    def execute_script(self, code: str, input_str: str = "") -> Dict[str, Any]:
        """Execute a script"""
        return self.executor.execute(code, input_str)
