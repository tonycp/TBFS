from ..business_data import HashTable, Repository

__all__ = ["HashService"]

class HashService:
    def __init__(self, repository: Repository[HashTable]):
        self.repository = repository

    def get_node_id(self, key: int) -> int | None:
        """Retrieve the node ID for a given key."""
        hash_entry = self.repository.get_query().filter_by(key=key).first()
        return hash_entry.node_id if hash_entry else None

    def add_entry(self, key: int, node_id: int) -> None:
        """Add a new entry to the hash table."""
        self.repository.create(HashTable(key=key, node_id=node_id))

    def remove_entry(self, key: int) -> None:
        """Remove an entry from the hash table."""
        hash_entry = self.repository.get_query().filter_by(key=key).first()
        if hash_entry:
            self.repository.delete(hash_entry)
