from data import *

FileInputTypes = {
    "name": str,
    "file_type": str,
    "size": int,
    "user_id": int
}

FileSourceInputTypes = {
    "file_id": int,
    "chunk_size": int,
    "chunk_number": int,
    "url": str
}

TagInputTypes = {
    "name": str
}

UserInputTypes = {
    "name": str,
    "is_connected": bool
}
