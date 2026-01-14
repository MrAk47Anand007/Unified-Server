import unittest
import shutil
import os
import time
from pathlib import Path
from script_runner import ScriptRunner

class TestScriptRunner(unittest.TestCase):
    def setUp(self):
        self.test_dir = "./test_scripts_env_final"
        self.runner = ScriptRunner(base_path=self.test_dir)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_path_traversal(self):
        self.runner.collection_manager.create_collection("Security")
        success = self.runner.save_script(
            name="../../evil",
            code="print('evil')",
            collection="Security"
        )
        self.assertFalse((Path(self.test_dir) / "evil.py").exists())
        self.assertTrue((Path(self.test_dir) / "Security" / "evil.py").exists())

    def test_timeout(self):
        code = "import time; time.sleep(5)"
        result = self.runner.executor.execute(code, timeout=1)
        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "Timeout exceeded")

    def test_dangerous_imports(self):
        code = "import os; print(os.name)"
        result = self.runner.executor.execute(code)
        self.assertFalse(result["success"])
        self.assertIn("Import of 'os' is not allowed", result["error"])

    def test_input_handling(self):
        code = "x = input(); print(f'Read: {x}')"
        input_str = "Secret Value"
        result = self.runner.executor.execute(code, input_str=input_str)
        self.assertTrue(result["success"])
        self.assertIn("Read: Secret Value", result["stdout"])

    def test_crud_operations(self):
        self.runner.collection_manager.create_collection("CRUD")
        self.runner.save_script("test", "print('hi')", "CRUD")
        loaded = self.runner.load_script("test", "CRUD")
        self.assertEqual(loaded["code"], "print('hi')")
        self.runner.delete_script("test", "CRUD")
        self.assertIsNone(self.runner.load_script("test", "CRUD"))

if __name__ == '__main__':
    unittest.main()
