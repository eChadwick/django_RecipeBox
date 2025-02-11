from pathlib import Path
from unittest import TestCase

class WeeklyBackupTests(TestCase):
    test_dir_path = 'test_dir'
    def setUp(self):
        Path(WeeklyBackupTests.test_dir_path).mkdir()

    def tearDown(self):
        Path(WeeklyBackupTests.test_dir_path).rmdir()
        
    def test_it_errors_if_db_is_invalid(self):
        pass