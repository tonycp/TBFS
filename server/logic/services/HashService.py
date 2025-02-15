import logging
from ..business_data import HashTable, Repository

__all__ = ["HashService"]


class HashService:
    def __init__(self, repository: Repository[HashTable]):
        self.repository = repository

    def get_node_id(self, key: int) -> int | None:
        """Retrieve the node ID for a given key."""
        logging.info(f"Getting node ID for key: {key}")
        hash_entry = self.repository.get_query().filter_by(key=key).first()
        node_id = hash_entry.node_id if hash_entry else None
        logging.info(f"Node ID for key {key}: {node_id}")
        return node_id

    def add_entry(self, key: int, node_id: int) -> None:
        """Add a new entry to the hash table."""
        logging.info(f"Adding entry with key: {key} and node ID: {node_id}")
        self.repository.create(HashTable(key=key, node_id=node_id))
        logging.info(f"Entry added with key: {key} and node ID: {node_id}")

    def remove_entry(self, key: int) -> None:
        """Remove an entry from the hash table."""
        logging.info(f"Removing entry with key: {key}")
        hash_entry = self.repository.get_query().filter_by(key=key).first()
        if hash_entry:
            self.repository.delete(hash_entry)
            logging.info(f"Entry removed with key: {key}")
        else:
            logging.warning(f"No entry found with key: {key}")
