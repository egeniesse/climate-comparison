import logging
import sqlite3

logger = logging.getLogger(__name__)

CREATE_ADAPTERS_TABLE = """
CREATE TABLE IF NOT EXISTS adapters (
	id integer PRIMARY KEY,
    guid text NOT NULL,
    type text NOT NULL
);"""


CREATE_ADAPTERS_INDEX = """
CREATE UNIQUE INDEX IF NOT EXISTS adapters_guid ON adapters(guid);
"""

CREATE_JOBS_TABLE = """
CREATE TABLE IF NOT EXISTS tasks (
	id integer PRIMARY KEY,
    guid text NOT NULL,
    state text NOT NULL,
	adapter integer NOT NULL,
	version integer NOT NULL,
    job_data text NOT NULL
);"""

CREATE_JOBS_INDEX = """
CREATE UNIQUE INDEX IF NOT EXISTS tasks_guid ON tasks(guid);
"""

CREATE_JOBS_STATE_INDEX = """
CREATE INDEX IF NOT EXISTS jobs_state ON tasks(adapter, state, version);
"""

CREATE_DATAPOINTS_TABLE = """
CREATE TABLE IF NOT EXISTS datapoints (
	id integer PRIMARY KEY,
    version integer NOT NULL,
    guid text NOT NULL,
    location integer NOT NULL,
    date integer NOT NULL,
    data_type text NOT NULL,
    data_value integer NOT NULL
);"""

CREATE_DATAPOINTS_INDEX = """
CREATE UNIQUE INDEX IF NOT EXISTS datapoints_guid ON datapoints(guid);
"""

CREATE_DATAPOINT_TYPE_INDEX = """
CREATE INDEX IF NOT EXISTS datapoint_type ON datapoints(data_type, version, location);
"""


class DBClient:
    def __init__(self, db_path):
        self._connection = sqlite3.connect(db_path)
        self._cursor = self._connection.cursor()
        self._init_db()
    
    def _execute(self, query):
        logger.debug(f"DB Query Statment: \n\n{query}")
        self._cursor.execute(query)

    def _init_db(self):
        self._execute(CREATE_ADAPTERS_TABLE)
        self._execute(CREATE_ADAPTERS_INDEX)
        self._execute(CREATE_JOBS_TABLE)
        self._execute(CREATE_JOBS_INDEX)
        self._execute(CREATE_JOBS_STATE_INDEX)
        self._execute(CREATE_DATAPOINTS_TABLE)
        self._execute(CREATE_DATAPOINTS_INDEX)
        self._execute(CREATE_DATAPOINT_TYPE_INDEX)

    def create_if_not_exists(self, table, data):
        self.bulk_create_if_not_exists(table, [data])

    def bulk_create_if_not_exists(self, table, data_list):
        records_created = 0
        for data in data_list:
            if self.select(table, {"guid": data["guid"]}):
                continue
            records_created += 1
            self._insert(table, data)
        logger.info(f"Inserting: {records_created}/{len(data_list)} new record(s) into {table}")
        self._connection.commit()

    def _insert(self, table, data):
        keys, values = [], []
        for key, value in data.items():
            keys.append(f"'{key}'")
            values.append(f"'{value}'")
        key_strings, value_strings = ", ".join(keys), ", ".join(values)
        insert_statement = f"INSERT INTO {table} ({key_strings}) VALUES ({value_strings})"        
        self._execute(insert_statement)
    
    def select(self, table, params, limit=None, selected="*"):
        select_clauses = self._create_select_clause(params)
        select_statement = f"SELECT {selected} FROM {table} WHERE {select_clauses}" + (f" LIMIT {limit}" if limit else "")
        self._execute(select_statement)
        columns = [prop[0] for prop in self._cursor.description]
        return [dict(zip(columns, row)) for row in self._cursor.fetchall()]
    
    def update(self, table, select_params, update_params):
        update_clauses = ", ".join([f'{key} = "{value}"' for key, value in update_params.items()])
        select_clauses = self._create_select_clause(select_params)
        update_statement = f"UPDATE {table} SET {update_clauses} WHERE {select_clauses}"
        self._execute(update_statement)
        self._connection.commit()
    
    def _create_select_clause(self, params):
        select_conditions = []
        for key, value in params.items():
            if type(value) == list:
                wrapped_values = ", ".join([f'"{val}"' for val in value])
                select_conditions.append(f'{key} IN ({wrapped_values})')
            else:
                select_conditions.append(f'{key} = "{value}"')
        return " AND ".join(select_conditions)
