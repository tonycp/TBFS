import asyncio, hashlib
from typing import List, Optional

from .chord_reference import ChordReference

__all__ = ["in_between", "bully", "hash_sha1_key", "join_nodes"]


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


async def join_nodes(
    node: Optional[ChordReference], nodes: List[Optional[ChordReference]]
) -> None:
    async def join_async(internal: Optional[ChordReference], sucs):
        await asyncio.to_thread(internal.join(sucs))

    task = []
    for internal in nodes:
        sucs = node.get_sucs(internal.id)
        task.append(join_async(internal, sucs))
    await asyncio.gather(*task)
