from enum import Enum
from data import *


class ELECTION(Enum):
    LEADER = 1
    FOLLOWER = 2
    CANDIDATE = 3


FileInputTypes = {
    "name": str,
    "file_type": str,
    "size": int,
    "user_id": int,
}

FileSourceInputTypes = {
    "file_id": int,
    "chunk_size": int,
    "chunk_number": int,
    "url": str,
}

TagInputTypes = {
    "name": str,
}

UserInputTypes = {
    "name": str,
    "is_connected": bool,
}
