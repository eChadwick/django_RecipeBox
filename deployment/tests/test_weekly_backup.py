import shutil
import sys
from unittest import TestCase
from pathlib import Path
import time

sys.path.append(str(Path(__file__).parent.parent))
from data_backup import daily_backup, MAX_DAILY_BACKUPS

DB_FILE_LOCATION = Path(__file__).parent.parent.parent / 'db.sqlite3'

class WeeklyBackupTests(TestCase):
    def setUp(self):
        self.source_dir = (Path(__file__).parent / "source_directory")
        self.source_dir.mkdir()
        self.destination_dir = (
            Path(__file__).parent / "destination_directory")
        self.destination_dir.mkdir()

    def tearDown(self):
        shutil.rmtree(self.source_dir)
        shutil.rmtree(self.destination_dir)        

    def test_it_errors_if_db_is_invalid(self):
        test_file_path = self.source_dir / "not_sql.txt"
        open(test_file_path, "w").close()

        with self.assertRaises(ValueError):
            daily_backup(source=test_file_path, destination=self.destination_dir)

    def test_it_copies_input_file_to_destination(self):
        daily_backup(source=DB_FILE_LOCATION, destination=self.destination_dir)
        self.assertTrue((self.destination_dir / 'db.sqlite3').is_file())

    def test_it_deletes_oldest_file_if_over_size_limit(self):
        for i in range(7):
            shutil.copy(DB_FILE_LOCATION , self.destination_dir / f'db_{i}')
            time.sleep(.1)
        
        daily_backup(source=DB_FILE_LOCATION, destination=self.destination_dir)
        
        self.assertEqual(len(list(self.destination_dir.iterdir())), MAX_DAILY_BACKUPS)
        self.assertFalse((self.destination_dir / 'db_0').is_file())