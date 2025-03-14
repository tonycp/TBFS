import json
from logic.business_services import ServerService
from data import File, Tag, User
from typing import Any, List, Dict, Tuple

import logging

from data.const import MAX_ITERATIONS

from .chord_reference import ChordReference
from .leader import ChordLeader
from .utils import hash_sha1_key

__all__ = ["LeaderService"]


class LeaderService(ServerService):
    def __init__(self, chord_server: ChordLeader):
        ServerService.__init__(self)
        self.chord_server = chord_server

    def _find_successors(
        self, key: str, num_successors: int = 3
    ) -> List[ChordReference]:
        """Find the successors of a key in the Chord ring."""
        successors = []
        iterations = MAX_ITERATIONS
        try:
            node = self.chord_server
            id = hash_sha1_key(key)
            while len(successors) < num_successors and iterations > 0:
                if node not in successors:
                    successors.append(node)
                node = node.get_sucs(id)
                id = node.id
                iterations -= 1
        except Exception as e:
            logging.error(f"Error finding successors for key {key}: {e}")
            successors = []
        logging.info(f"Successors for key {key}: {successors}")
        return successors

    def _replicate_data(
        self,
        header: Tuple[str, str, List[str]],
        data: Dict[str, Any],
        nodes: List[ChordReference],
    ) -> None:
        """Replicate data to the specified nodes in a Chord ring."""
        logging.info(f"Replicating data to nodes: {nodes}")
        resp = []
        for node in nodes:
            try:
                response = self.chord_server.send_request_message(
                    node,
                    header,
                    data,
                    self.chord_server.data_port,
                )
                logging.info(f"Data replicated to node: {node}, response: {response}")
                obj: Dict[str, Any] = json.loads(response)
                if not obj.get("error"):
                    resp.append(response)
            except Exception as e:
                logging.error(f"Error replicating data to node {node}: {e}")

        return resp

    def create_update_file(
        self, header: Tuple[str, str, List[str]], file: File, tags: List[str]
    ) -> File:
        """Create or update a file and replicate the data."""
        result = ServerService.create_update_file(self, file, tags)
        data = {"file": file, "tags": tags}
        nodes = self._find_successors(file.name)
        self._replicate_data(data, nodes)
        return result

    def delete_file_by_tags(
        self, header: Tuple[str, str, List[str]], tag_query: List[str]
    ) -> None:
        """Delete files by tags and replicate the data."""
        nodes = self._find_successors("".join(tag_query))
        for node in nodes:
            # Implement logic to delete data from the node
            pass
        ServerService.delete_file_by_tags(self, tag_query)
        data = {"tag_query": tag_query}
        self._replicate_data(data, nodes)

    def get_files_by_tags(
        self, header: Tuple[str, str, List[str]], tag_query: List[str]
    ) -> List[File]:
        """Get files by tags."""
        nodes = self._find_successors("".join(tag_query))
        files = []
        for node in nodes:
            # Implement logic to get data from the node
            pass
        return files

    def add_tags_to_files(
        self, header: Tuple[str, str, List[str]], tag_query: List[str], tags: List[str]
    ) -> None:
        """Add tags to files and replicate the data."""
        ServerService.add_tags_to_files(self, tag_query, tags)
        data = {"tag_query": tag_query, "tags": tags}
        nodes = self._find_successors("".join(tag_query))
        self._replicate_data(data, nodes)

    def delete_tags_from_files(
        self, header: Tuple[str, str, List[str]], tag_query: List[str], tags: List[str]
    ) -> None:
        """Delete tags from files and replicate the data."""
        ServerService.delete_tags_from_files(self, tag_query, tags)
        data = {"tag_query": tag_query, "tags": tags}
        nodes = self._find_successors("".join(tag_query))
        self._replicate_data(data, nodes)

    def get_user_id(self, header: Tuple[str, str, List[str]], user_name: str) -> int:
        """Get user ID."""
        return ServerService.get_user_id(self, user_name)
