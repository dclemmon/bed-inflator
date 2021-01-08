#! /Users/cameron/code/bt_play/bin/python
"""
This module connects to, and changes the number of my adjustable bed
"""

import asyncio
import datetime
import time

from bleak import BleakClient
from bleak.exc import BleakError

import caffeine

MAC_ADDR = "6D5BD55A-F8DD-4546-B18E-3B5F6565EC34"
READ_CHARACTERISTIC = "FFFFD1FD-388D-938B-344A-939D1F6EFEE1"
WRITE_CHARACTERISTIC = "FFFFD1FD-388D-938B-344A-939D1F6EFEE2"

COMMAND_STRINGS = [
    "161602538c532c02538c1102003c12ae",  # 3c is 60 in hex
    "161602538c532c02538c1102003712a9",  # 37 is 55 in hex
]

def notification_handler(sender, data):
    """
        Write any responses from the READ_CHARACTERISTIC to file in case we
        need them
    """
    with open("./dump.txt", 'a') as temp_file:
        temp_file.write(str(data) + "\n")

async def send_commands(address: str):
    """
        Send commands to the device
    """
    async with BleakClient(address) as client:
        global COMMAND_STRINGS
        await client.start_notify(
            READ_CHARACTERISTIC, notification_handler,
        )
        input_str = COMMAND_STRINGS.pop(0)
        COMMAND_STRINGS.append(input_str)

        bytes_to_send = bytearray.fromhex(input_str)

        while not await client.is_connected():
            await asyncio.sleep(1)

        await client.write_gatt_char(WRITE_CHARACTERISTIC, bytes_to_send)
        timestamp = datetime.datetime.now()
        print(f"{timestamp} - Sent: {input_str}")


if __name__ == "__main__":
    time_delay = datetime.timedelta(hours=1)
    run_time = datetime.datetime.now() - time_delay
    while True:
        if datetime.datetime.now() - run_time >= time_delay:
            try:
                loop = asyncio.get_event_loop()
                loop.run_until_complete(send_commands(MAC_ADDR))
                run_time = datetime.datetime.now()
            except BleakError as e:
                print("Failed to execute with error: ", e)
        time.sleep(5)
