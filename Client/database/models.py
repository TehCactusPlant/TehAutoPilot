import os
import sqlite3 as db
from abc import abstractmethod, ABC
import logging

import numpy

logger = logging.getLogger(__name__)


class ColumnType:
    INTEGER = "INTEGER"
    REAL = "REAL"
    TEXT = "TEXT"
    BLOB = "BLOB"
    NULL = "NULL"


class ForeignKey:
    def __init__(self, table, col):
        self.table = table
        self.column = col


class Column:
    name = ""
    foreign_key = (False, "", "")
    primary_key = False
    entry_type = "INTEGER"

    def __init__(self, name, entry_type,
                 foreign_key: ForeignKey = None, primary_key=False,
                 auto_inc=False, is_unique=False, co_unique=False):
        self.name = name
        self.entry_type = entry_type
        self.primary_key = primary_key
        self.auto_inc = auto_inc
        self.is_unique = is_unique
        self.co_unique = co_unique
        self.foreign_key = foreign_key


class Table:
    columns: list[Column] = []

    def __init__(self, name, columns: list):
        self.name = name
        self.columns = columns
        self.unique = ""

    def prevent_unique_pair(self):
        cols = []
        for col in self.columns:
            if col.co_unique:
                cols.append(col.name)
        if len(cols) > 0:
            self.unique = f", UNIQUE{tuple(cols)}"

    def _assemble_statement(self):
        statement = f"CREATE TABLE {self.name}("
        foreign_keys = ""
        co_uniques = []
        for i in range(len(self.columns)):
            col = self.columns[i]
            statement += f"{col.name} {col.entry_type}"
            if col.primary_key:
                statement += " PRIMARY KEY"
            if col.is_unique:
                statement += " UNIQUE"
            if col.co_unique:
                co_uniques.append(col.name)
            if col.foreign_key is not None:
                foreign_keys += f", FOREIGN KEY({col.name}) " \
                                + f"REFERENCES {col.foreign_key.table}" \
                                + f"({col.foreign_key.column})"

            if i == len(self.columns) - 1:
                if len(co_uniques) > 1:
                    co_uniques = tuple(co_uniques)
                    self.unique = f", UNIQUE{co_uniques}"
                statement += self.unique
                statement += foreign_keys
                statement += ")"
            else:
                statement += ", "
        return statement

    def create_table(self, database_file):
        con, cur = _connect_db(database_file)
        statement = self._assemble_statement()
        logger.info(f"Executing Statement: {statement}")
        cur.execute(statement)
        con.commit()
        _disconnect_db(con, cur)


class DBModel(ABC):
    def __init__(self, _id, db_name, table_name):
        self._id = _id
        self.db_host = db_name
        self.table_name = table_name
        self.secondary_table = None
        self.file_folder = ""

    def get_id(self):
        return self._id

    def set_id(self, _id):
        self._id = _id

    @abstractmethod
    def delete(self):
        raise NotImplemented

    @abstractmethod
    def save(self):
        raise NotImplemented

    @abstractmethod
    def get(self):
        raise NotImplemented

    def new_id_from_db(self, data):
        if self.get_id() is None and len(data) > 0:
            self.set_id(data[0]["_id"])
            logger.debug(f"New ID registered for entity {type(self)} in {self.table_name}: {self.get_id()}")

    def save_numpy(self, f_name,array):
        if self._id is not None:
            dir = os.path.dirname(self.db_host) + f"\\{self.file_folder}"
            logger.debug("Saving numpy array to " + f"{dir}\\{f_name}.npy")
            numpy.save(f"{dir}\\{f_name}.npy", array)
        else:
            logger.error(f"Numpy array not saved. Entity of type({type(self)} has no _id)")

    def load_numpy(self, f_name):
        if self._id is not None:
            dir = os.path.dirname(self.db_host) + f"\\{self.file_folder}"
            logger.debug("Loading numpy array at " + f"{dir}\\{f_name}.npy")
            return numpy.load(f"{dir}\\{f_name}.npy")
        else:
            logger.error(f"Numpy array not loaded. Entity of type({type(self)} has no _id)")


def bool_to_int(b: bool):
    return 1 if b else 0


def int_to_bool(i: int):
    return True if i == 1 else False


def parse_values_by_key(parse_list:list[dict], key:str, none_override=None):
    return parse_values_by_keys(parse_list, [key], none_override)


def parse_values_by_keys(parse_list: list[dict], keys: list, none_override=None):
    n_entries = []
    for key in keys:
        logger.debug(key)
        n_entry = [item[key] for item in parse_list]
        logger.debug(n_entry)
        for entry in n_entry:
            if entry is None:
                entry = none_override
        n_entries.extend(n_entry)
    return (n_entries[0], n_entries[0]) if len(n_entries) == 1 else tuple(n_entries)


def execute_query(db_file, statement, args=None):
    con, cur = _connect_db(db_file)
    if args is None:
        logger.debug(f"Executing Statement: {statement}:")
        sql_res = cur.execute(statement).fetchall()
    else:
        logger.debug(f"Executing Statement: {statement} with args {args}:")
        sql_res = cur.execute(statement, args).fetchall()
    resp = []
    for row in sql_res:
        resp.append({key: row[key] for key in row.keys()})
    con.commit()
    _disconnect_db(con, cur)
    return resp


def dict_from_row(row):
    return dict(zip(row.keys(), row))


def _connect_db(database_file):
    con = db.connect(database_file)
    con.row_factory = db.Row
    cur = con.cursor()
    return con, cur


def _disconnect_db(con, cur):
        cur.close()
        con.close()
