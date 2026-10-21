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
        """Create or update a state record."""
        logger.debug(f"Updating state for '{name}' to '{state}'")
        self.cursor.execute('INSERT OR REPLACE INTO states (name, state) values (?, ?)', (name, state))
        self.conn.commit()


    def get_state(self, name):
        """This function retrieves the state string for a given plugin from the database. It executes a SQL query to fetch the state from the "states" table based on the provided plugin name.
        Input-Output Arguments
        :param self: State. An instance of the State class.
        :param name: String. The name of the plugin for which the state is to be retrieved.
        :return: String. The state string for the given plugin. If no state is found, it returns None.
        """