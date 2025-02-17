from typing import Any, List, Optional, Dict, Union

import threading, json, logging, time

from dist.chord_reference import ChordReference
from dist.chord import ChordNode
from logic.handlers import *
from data.const import *

from .server import Server

__all__ = ["ChordServer"]


class ChordServer(Server, ChordNode):
    def __init__(self, config: Optional[Dict[str, Optional[Union[str, int]]]] = None):
        Server.__init__(self, config)
        ChordNode.__init__(self, config)

    # region Request Methods
    def _is_leader_request(self, last_endpoint: str) -> bool:
        """Check if the request is from the leader based on the endpoint."""
        leader_port = self._config.get(NODE_PORT_KEY)
        return last_endpoint.endswith(f":{leader_port}")

    def _solver_request(
        self, header_str: str, rest_mesg: List[str], last_endpoint: str
    ) -> str:
        """Solve the request and return the result."""
        logging.info(f"Received a message from: {last_endpoint}")

        while not self.leader.is_alive:
            logging.warning("Leader is dead, waiting for new leader...")
            time.sleep(WAIT_CHECK * START_MOD)

        is_leader_req = self._is_leader_request(last_endpoint)

        if not self.im_the_leader and not is_leader_req:
            node, port = self.leader, self.data_port
            return self.send_request_message(node, header_str, rest_mesg, port)
        if is_leader_req:
            return handle_request(header_str, rest_mesg)
        return self._handle_leader_request(header_str, rest_mesg)

    def _handle_leader_request(self, header_str: str, rest_mesg: List[str]) -> str:
        """Handle the request as the leader and aggregate responses from other nodes."""
        header = parse_header(header_str)
        data = json.loads(rest_mesg[0].decode("utf-8"))

        resp = handle_request(header, data)
        all_resp = self._aggregate_data_from_nodes(header_str, rest_mesg, resp)
        # Process the request with the aggregated data
        return all_resp

    def _aggregate_data_from_nodes(
        self, header_str: str, rest_mesg: List[str], resp: str
    ) -> Dict[str, Any]:
        """Aggregate data from other nodes."""
        aggregated_data = {}
        self._update_data(aggregated_data, resp)

        # Notify all nodes and collect their responses
        for node in self._get_all_nodes():
            port = node.data_port
            response = self.send_request_message(node, header_str, rest_mesg, port)
            self._update_data(aggregated_data, response)

        return aggregated_data

    def _update_data(self, aggregated_data: Dict[str, Any], response: str) -> None:
        """Update the aggregated data with the response."""
        response_data = json.loads(response)
        for key, value in response_data.items():
            if key in aggregated_data:
                aggregated_data[key].update(value)
            else:
                aggregated_data[key] = value

    def _get_all_nodes(self) -> List[ChordReference]:
        """Get a list of all nodes in the network."""
        if self.successor.id == self.id:
            return []

        nodes = [self.successor]
        current_node = self.successor

        while current_node != self:
            nodes.append(current_node.successor)
            current_node = current_node.successor

        return nodes

    # endregion

    def run(self) -> None:
        # Start threads
        ChordNode.run(self)
        Server.run(self)
