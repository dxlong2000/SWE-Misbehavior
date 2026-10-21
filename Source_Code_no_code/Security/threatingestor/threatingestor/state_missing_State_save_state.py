import sqlite3
from loguru import logger

import threatingestor.exceptions

class State:
    """State DB management."""
    def __init__(self, dbname):
        """Set up a connection to the state DB."""
        try:
            self.conn = sqlite3.connect(dbname)
            self.cursor = self.conn.cursor()
            self._create_table()
        except sqlite3.Error:
            raise threatingestor.exceptions.IngestorError("State database seems broken")


    def _create_table(self):
        """Create table if it doesn't already exist."""
        self.cursor.execute('CREATE TABLE IF NOT EXISTS states (name text UNIQUE, state text)')
        self.conn.commit()


    def save_state(self, name, state):
        """This function is used to create or update a state record in a database. It takes a name and state as input parameters, and inserts or replaces the corresponding values in the "states" table of the database.
        Input-Output Arguments
        :param self: State. An instance of the State class.
        :param name: String. The name of the state record.
        :param state: Any data type. The state value to be stored.
        :return: No return values.
        """


    def get_state(self, name):
        """Return the state string for a given plugin."""
        logger.debug(f"Getting state for '{name}'")
        self.cursor.execute('SELECT state FROM states WHERE name=?', (name,))
        res = self.cursor.fetchone()
        return res[0] if res else res