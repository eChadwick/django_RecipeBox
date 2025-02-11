from pathlib import Path
from unittest import TestCase

class WeeklyBackupTests(TestCase):
    def setUp(self):
        self.test_dir = (Path(__file__).parent / f"test_directory")
        self.test_dir.mkdir()

    def tearDown(self):
        pass
        Path(self.test_dir).rmdir()
        
    def test_it_errors_if_db_is_invalid(self):
        pass