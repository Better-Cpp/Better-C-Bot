import sqlite3
from pathlib import Path

class Database:
    def __init__(self, path: Path):
        self.connection = sqlite3.connect(path)
        self.cursor = self.connection.cursor()

        self.cursor.executescript((Path(__file__).parent.parent / "init.sql").read_text())
        self.connection.commit()

    def get_user_field(self, field_name, user_id):
        cursor = self.cursor.execute(f"SELECT {field_name} FROM users WHERE id = ?", [user_id])
        return cursor.fetchone()[0]
    
    def get_money_leaderboard(self, max_entries):
        cursor = self.cursor.execute(f"SELECT id, money FROM users ORDER BY money DESC LIMIT ?", [max_entries])
        return cursor.fetchall()
    
    def set_user_field(self, field_name, value, user_id, commit_changes = True, add_value_instead = False):
        self.cursor.execute(f"UPDATE users SET {field_name} = {(field_name + ' +') if add_value_instead else ''} ? WHERE id = ?", [value, user_id])
        if commit_changes:
            self.connection.commit()

    def check_user(self, user_id):
        """
        NOTE: This function only checks if a user ID exists in the database, not if the user ID belongs to a valid server member.
        """
        # Query number of times user id is found which should be 0 or 1.
        cursor = self.cursor.execute("SELECT COUNT(*) FROM users WHERE id = ?", [user_id])
        count = cursor.fetchone()[0]

        # If no user ID was found in database, add user.
        if count == 0:
            self.cursor.execute("INSERT INTO users VALUES (?, 0, 0)", [user_id])
            self.connection.commit()
        elif count > 1:
            raise Exception(f"Found multiple copies of user ID ({user_id}) in database.")
