import logging
import sqlite3
import sys
from abc import ABCMeta, abstractmethod

from .queries import Format

logger = logging.getLogger(__name__)

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
handler.setLevel(logging.DEBUG)

logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


class BaseDB(metaclass=ABCMeta):
    """ Abstract Database Class. """

    @abstractmethod
    def connect(self):
        """ Create the connection to the database. """

    @abstractmethod
    def close(self):
        """ End the connection to the database. """

    @abstractmethod
    def execute(self, cmd, *args, **kwargs):
        """ Execute a command to the database. """

    @abstractmethod
    def commit(self):
        """ Write changes to the database. """


class SQLiteManager:
    """ SQLite Database Manager. """

    def __init__(self, db):
        self.db = db

    def all(self, model):
        """
        Get all entries from a model(table).

        :return: all entries
        :rtype: list
        """
        return self.db.execute(f"SELECT * FROM {model}").fetchall()

    def filter(self, model, **kwargs):
        """
        Filter all entries from a model(table).

        :return: filtered entries
        :rtype: list
        """
        """ Filter all entries from a model(table). """
        conditions = []
        for raw_field, raw_value in kwargs.items():
            formatter = Format(raw_field, raw_value)
            field_class = formatter.get_format_class()
            conditions.append(field_class.get_string())

        ## final query
        sql_conditions = " AND ".join(conditions)
        query = f"SELECT * FROM {model} WHERE {sql_conditions}"
        logger.debug(f"SQL => {query}")
        return self.db.execute(query).fetchall()


class SQLiteDB(BaseDB):
    """ SQLite Database. """

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self._connection = None
        self.connected = False

        # managers
        self.manager = SQLiteManager(self)

    def connect(self):
        """ Create the connection to the SQLite database. """
        if self.connected:
            return self._connection
        self._connection = sqlite3.connect(*self.args, **self.kwargs)
        # self._connection.row_factory = sqlite3.Row
        self.connected = True
        return self._connection

    def close(self):
        """ End the connection to the SQLite database. """
        if self.connected:
            self._connection.close()
        self.connected = False

    def execute(self, sql, *args):
        """ Execute a command to the SQLite database. """
        return self._connection.execute(sql, args)

    def commit(self):
        """ Write changes to the SQLite database. """
        self._connection.commit()

    def executemany(self, sql, data):
        return self._connection.executemany(sql, data)
