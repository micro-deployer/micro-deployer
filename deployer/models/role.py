from pathlib import Path
from typing import List

from cue import CueDict


class Role:
    name: str
    sources: List[Path]


class RoleDict(CueDict):
    # FIXME deleting a role is not allowed if any device has the role
    pass
