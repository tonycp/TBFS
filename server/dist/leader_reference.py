from typing import Optional

from dist.chord_reference import ChordReference
from logic.configurable import Configurable


class LeaderReference(ChordReference):
    def __init__(self, config: Configurable):
        ChordReference.__init__(self, config)

    # region Properties
    @property
    def leader(self) -> ChordReference:
        return self._get_chord_reference("leader")

    @property
    def im_the_leader(self) -> bool:
        return self._get_property("im_the_leader")

    @property
    def in_election(self) -> bool:
        return self._get_property("in_election")

    @leader.setter
    def leader(self, node: ChordReference):
        self._set_chord_reference("leader", node.id)

    @im_the_leader.setter
    def im_the_leader(self, value: bool):
        self._set_property("im_the_leader", value)

    @in_election.setter
    def in_election(self, value: bool):
        self._set_property("in_election", value)

    # endregion

    # region Chord Methods
    def adopt_leader(self, node: Optional[ChordReference] = None) -> None:
        self._call_notify_methods("adopt_leader", node)

    # endregion
