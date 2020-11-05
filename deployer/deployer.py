import asyncio
from operator import attrgetter
import os
from pathlib import Path
import struct
from typing import AsyncIterator, Iterator, List


async def deploy(device):
    device.deployment_progress = 0

    _, writer = await asyncio.open_connection(
        device.ip, device.port
    )

    for filepath in _write(writer, device.root_path):
        device.deployment_progress += 1

    writer.close()
    await writer.drain()
    await writer.wait_closed()


def _write(writer, root_path: Path) -> Iterator[Path]:
    paths = [path for path in root_path.glob('**/*') if path.is_file()]
    files_count = len(paths)
    files_count_bytes = struct.pack('>B', files_count)
    writer.write(files_count_bytes)
    for filepath in paths:
        relative_path = filepath.relative_to(root_path)
        yield relative_path
        filepath_bytes = str(relative_path).encode()
        filepath_length_bytes = struct.pack('>B', len(filepath_bytes))
        writer.write(filepath_length_bytes)
        writer.write(filepath_bytes)
        with filepath.open('rb') as f:
            file_length = os.fstat(f.fileno()).st_size
            file_length_bytes = struct.pack('>H', file_length)
            writer.write(file_length_bytes)
            writer.write(f.read())
