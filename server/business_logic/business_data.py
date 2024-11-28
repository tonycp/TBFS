from datetime import datetime
from data_access import *

FileInputTypes = {
    "name": str,
    "file_type": str,
    "size": int,
    "user_id": int,
    "creation_date": datetime,
    "update_date": datetime,
}

FileSourceInputTypes = {
    "file_id": int,
    "chunk_size": int,
    "chunk_number": int,
    "url": str,
    "creation_date": datetime,
    "update_date": datetime,
}

TagInputTypes = {
    "name": str,
    "creation_date": datetime,
    "update_date": datetime,
}

UserInputTypes = {
    "name": str,
    "is_connected": bool,
    "creation_date": datetime,
    "update_date": datetime,
}
