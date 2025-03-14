import hashlib

__all__ = ["in_between", "bully", "hash_sha1_key"]


def in_between(k: int, start: int, end: int) -> bool:
    """Check if an id is between two other ids in the Chord ring."""
    if start < end:
        return start < k <= end
    else:
        return start < k or k <= end


def bully(id: int, other_id: int) -> bool:
    """Check if the current node is more powerful than the other node."""
    return int(id) > int(other_id)


def hash_sha1_key(key: str) -> int:
    return int(hashlib.sha1(key.encode("utf-8")).hexdigest(), 16)
