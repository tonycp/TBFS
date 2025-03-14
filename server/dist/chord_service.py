from sqlalchemy import MetaData, create_engine, select
from typing import Any, List, Dict, Optional
from datetime import datetime


from data.const import *
from logic.configurable import Configurable
from dist.chord import ChordNode
from dist.chord_reference import replication


__all__ = ["ChordService"]


class ChordService:
    def __init__(self, _chord_node: ChordNode, config: Optional[Configurable]):
        self._chord_node = _chord_node
        self._config = config or Configurable()
        self.change_engine()

    def _get_metadata(self):
        metadata = MetaData()
        metadata.reflect(bind=self.engine)
        return metadata

    def change_engine(self, database_url: Optional[str] = None):
        database_url = database_url or self._config[DB_URL_KEY]
        self.engine = create_engine(database_url)

    def get_records_by_table(
        self,
        table_name: str,
        last_timestamp: datetime = None,
        metadata: MetaData = None,
    ) -> List[Dict[str, Any]]:
        metadata = metadata or MetaData()
        table = metadata.tables.get(table_name)
        if table:
            query = select(table)
            if last_timestamp:
                query = query.where(table.c.last_modified >= last_timestamp)
            with self.engine.connect() as conn:
                records = conn.execute(query).fetchall()
            return list(map(dict, records))

    def get_all_records(
        self, last_timestamp: datetime = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        metadata = MetaData()
        result = {}
        for table_name in metadata.tables.keys():
            records = self.get_records_by_table(table_name, last_timestamp, metadata)
            result[table_name] = records
        return result

    def set_record_by_table(
        self,
        table_name: str,
        record: Dict[str, Any],
        metadata: MetaData = None,
    ) -> None:
        metadata = metadata or MetaData()
        table = metadata.tables.get(table_name)
        if table:
            with self.engine.connect() as conn:
                query = select(table).where(table.c.id == record["id"])
                if not conn.execute(query.exists()):
                    conn.execute(table.insert(), record)
                elif query.c.last_modified < record["last_modified"]:
                    conn.execute(table.update(), record)

    def set_records_by_table(
        self,
        table_name: str,
        records: List[Dict[str, Any]],
        metadata: MetaData = None,
    ) -> None:
        metadata = metadata or MetaData()
        for record in records:
            self.set_record_by_table(table_name, record, metadata)

    def set_all_records(
        self,
        tables_records: Dict[str, List[Dict[str, Any]]],
        metadata: MetaData = None,
    ) -> None:
        metadata = metadata or MetaData()
        for table_name, records in tables_records.items():
            self.set_records_by_table(table_name, records, metadata)

    def replication(self, last_timestamp: Optional[datetime] = None):
        replics = self._chord_node.get_replications()
        for dest, name in replics:
            replication(dest, self._chord_node, name, last_timestamp=last_timestamp)
