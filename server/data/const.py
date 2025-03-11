from enum import Enum

# -*- coding: utf-8 -*-
# Constants for the server logic

# Keys for data storage
PROTOCOL_KEY = "protocol"
HOST_KEY = "host"
PORT_KEY = "port"
NODE_PORT_KEY = "chord_port"
MCAST_ADDR_KEY = "mcast_addr"

# Environment variable keys
PROTOCOL_ENV_KEY = "PROTOCOL"
HOST_ENV_KEY = "HOST"
PORT_ENV_KEY = "PORT"
NODE_PORT_ENV_KEY = "CHORD_PORT"
MCAST_ADDR_ENV_KEY = "MCAST_ADDR"

# Default values
DEFAULT_PROTOCOL = "tcp"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_DATA_PORT = 10000
DEFAULT_NODE_PORT = 10001
DEFAULT_ELECTION_PORT = 10002
DEFAULT_BROADCAST_PORT = 10003
DEFAULT_MCAST_ADDR = "224.0.0.1"

# Chord constants
SHA_1 = 160
BATCH_SIZE = 20
WAIT_CHECK = 5
START_MOD = 0.05
BROADCAST_MOD = 0.25
STABLE_MOD = 2
ELECTION_MOD = 0.1
ELECTION_TIMEOUT = 10
MAX_ITERATIONS = 3


# Commands for the Chord protocol
class ELECTION(Enum):
    START = 1
    WINNER = 2
    OK = 3


ELECTION_COMMANDS = {
    ELECTION.START: {
        "command_name": "Election",
        "function": "election_call",
        "dataset": ["id", "ip"],
    },
    ELECTION.WINNER: {
        "command_name": "Election",
        "function": "winner_call",
        "dataset": ["id", "ip"],
    },
    ELECTION.OK: {
        "command_name": "Election",
        "function": "ok_call",
        "dataset": ["id", "ip"],
    },
}


class CHORD_DATA(Enum):
    GET_PROPERTY = 1
    SET_PROPERTY = 2
    GET_CHORD_REFERENCE = 1
    SET_CHORD_REFERENCE = 2
    FIND_CALL = 3
    NOTIFY_CALL = 4
    PON_CALL = 5
    JOIN_CALL = 6


CHORD_DATA_COMMANDS = {
    CHORD_DATA.GET_PROPERTY: {
        "command_name": "Chord",
        "function": "get_property_call",
        "dataset": ["property"],
    },
    CHORD_DATA.GET_CHORD_REFERENCE: {
        "command_name": "Chord",
        "function": "get_chord_reference_call",
        "dataset": ["property"],
    },
    CHORD_DATA.SET_PROPERTY: {
        "command_name": "Chord",
        "function": "set_property_call",
        "dataset": ["property", "value"],
    },
    CHORD_DATA.SET_CHORD_REFERENCE: {
        "command_name": "Chord",
        "function": "set_chord_reference_call",
        "dataset": ["property", "ip"],
    },
    CHORD_DATA.FIND_CALL: {
        "command_name": "Chord",
        "function": "finding_call",
        "dataset": ["function_name", "key"],
    },
    CHORD_DATA.NOTIFY_CALL: {
        "command_name": "Chord",
        "function": "notify_call",
        "dataset": ["function_name", "node"],
    },
    CHORD_DATA.PON_CALL: {
        "command_name": "Chord",
        "function": "pon_call",
        "dataset": ["message"],
    },
}
