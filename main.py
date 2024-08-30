import asyncio
from module_broker import BrokerClient
from module_transcriber import Transcriber
from module_config import ConfigManager


async def main():
    try:
        app_config = ConfigManager()
        queue_name = "converted_files_queue"
        transcribe_client = Transcriber()
        broker_client = BrokerClient(app_config, queue_name, transcribe_client)
        await broker_client.receive_message()
        # asyncio.create_task(broker_client.receive_message(queue_name))
    except Exception as e:
        raise e


if __name__ == "__main__":
    asyncio.run(main())
