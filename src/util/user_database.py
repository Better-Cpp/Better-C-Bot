import sqlite3

user_database_connection = sqlite3.connect('users.db')
user_database = user_database_connection.cursor()

user_database.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER, money INTEGER, last_daily_timestamp INTEGER)')
user_database_connection.commit()

def user_database_get(field_name, user_id):
    query = user_database.execute(f'SELECT {field_name} FROM users WHERE id = ?', [user_id])
    return query.fetchone()[0]

def user_database_set(field_name, value, user_id, commit_changes = True, add_value_instead = False):
    user_database.execute(f'UPDATE users SET {field_name} = {(field_name + " +") if add_value_instead else ""} ? WHERE id = ?', [value, user_id])
    if commit_changes:
        user_database_connection.commit()

def user_database_check_if_user_exists_otherwise_add(user_id):
    """
    NOTE: This function only checks if a user ID exists in the database, not if the user ID belongs to a valid server member.
    """
    # Query number of times user id is found which should be 0 or 1.
    query = user_database.execute('SELECT COUNT(*) FROM users WHERE id = ?', [user_id])
    count = query.fetchone()[0]

    # If no user ID was found in database, add user.
    if count == 0:
        user_database.execute('INSERT INTO users VALUES (?, 0, 0)', [user_id])
        user_database_connection.commit()
    elif count > 1:
        raise Exception(f'Found multiple copies of user ID ({user_id}) in database.')