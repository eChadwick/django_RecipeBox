import sqlite3

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
    db_cursor.execute('select name from sqlite_master;')
    results = db_cursor.fetchall()

    if(not EXPECTED_TABLES.issubset(set(results))):
        raise ValueError('Something is amiss with the input database')