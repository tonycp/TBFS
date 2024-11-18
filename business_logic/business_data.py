from datetime import datetime
from ..data_access import *

FileInputTypes = {
    "name": str,
    "file_type": str,
    "size": int,
    "user_id": int,
    "creation_date": datetime,
    "update_date": datetime,
}
