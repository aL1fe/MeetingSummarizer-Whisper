import os
from dotenv import load_dotenv
from module_broker import BrokerClient
from module_transcriber import Transcriber
import asyncio


async def main():
    try:
        queue_name = "converted_files_queue"
        transcribe_client = Transcriber()
        broker_client = BrokerClient(queue_name, transcribe_client)
        await broker_client.receive_message()
    except Exception as e:
        raise e


if __name__ == "__main__":
    asyncio.run(main())
