import shutil
import sqlite3

MAX_DAILY_BACKUPS = 7

EXPECTED_TABLES = {
    'recipe_app_ingredient',
    'recipe_app_recipeingredient',
    'recipe_app_recipe',
    'recipe_app_tag',
    'recipe_app_recipe_tags'
}

def daily_backup(source, destination):
    db = sqlite3.connect(source)
    db_cursor = db.cursor()
    db_cursor.execute('select name from sqlite_master where type=="table";')
    results = db_cursor.fetchall()

    actual_tables = {row[0] for row in results}

    if(not EXPECTED_TABLES.issubset(actual_tables)):
        raise ValueError('Something is amiss with the input database')
    
    db.close()

    shutil.copy(source, destination)
    
    # Get all the files with the oldest first
    files = sorted([file for file in destination.iterdir()], key = lambda file: file.stat().st_ctime)

    while len(files) > MAX_DAILY_BACKUPS:
        delete_file = files.pop(0)
        delete_file.unlink()
    
