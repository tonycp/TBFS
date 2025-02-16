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
DEFAULT_HOST = "localhost"
DEFAULT_DATA_PORT = 5555
DEFAULT_NODE_PORT = 5556
DEFAULT_MCAST_ADDR = "225.0.0.1"

# Chord constants
SHA_1 = 160
BATCH_SIZE = 20
WAIT_CHECK = 5
STABLE_MOD = 2
ELECTION_MOD = 0.1
ELECTION_TIMEOUT = 10