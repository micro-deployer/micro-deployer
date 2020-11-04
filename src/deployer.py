import asyncio
import os
import struct


async def deploy(device):
    device.deployment_progress = 0
    for i in range(100):
        await asyncio.sleep(0.1)
        device.deployment_progress += 1
    return

    reader, writer = await asyncio.open_connection(
        device.ip, device.port
    )
    filepaths = [device.name]

    files_count_bytes = struct.pack('>B', len(filepaths))
    writer.write(files_count_bytes)
    for filepath in filepaths:
        device.deployment_progress += 1
        filepath_length_bytes = struct.pack('>B', len(filepath))
        writer.write(filepath_length_bytes)
        filepath_bytes = filepath.encode()
        writer.write(filepath_bytes)
        with open(filepath, 'rb') as f:
            file_length = os.fstat(f.fileno()).st_size
            file_length_bytes = struct.pack('>H', file_length)
            writer.write(file_length_bytes)
            writer.write(f.read())

    writer.close()
    await writer.drain()
    await writer.wait_closed()
