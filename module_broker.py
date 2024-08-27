import asyncio
import aio_pika
import aio_pika.abc
import os
from dotenv import load_dotenv
from module_transcriber import Transcriber


class BrokerClient:
    def __init__(self, queue_name, pipe, loop):
        self.__queue_name = queue_name
        self.__pipe = pipe
        self.__loop = loop
        #  Load environment variables from .env file
        self.__broker_host = os.getenv('MESSAGE_BROKER_HOST', '127.0.0.1')
        self.__broker_login = os.getenv('MESSAGE_BROKER_LOGIN')
        self.__broker_password = os.getenv('MESSAGE_BROKER_PASSWORD')

    async def __connect_to_broker(self):
        # Establishing a connection to RabbitMQ
        connection = await aio_pika.connect_robust(
            host=self.__broker_host,
            port=5672,
            virtualhost='/',
            login=self.__broker_login,
            password=self.__broker_password,
            loop=self.__loop
        )
        return connection

    async def receive_message(self):
        connection = await self.__connect_to_broker()
        async with connection:
            queue_name = self.__queue_name

            # Creating channel
            channel: aio_pika.abc.AbstractChannel = await connection.channel()

            # Declaring queue
            queue: aio_pika.abc.AbstractQueue = await channel.declare_queue(
                queue_name,
                auto_delete=False,
                durable=True
            )

            async with queue.iterator() as queue_iter:
                # Cancel consuming after __aexit__
                async for message in queue_iter:
                    async with message.process():
                        print(f"Received: {message.body.decode()}")

                        # if app runs on the local host switch folder
                        if self.__broker_host == '127.0.0.1':
                            file_folder = os.getenv('CONVERTER_FOLDER_CONVERTED_FILES')
                            file_name = os.path.basename(message.body.decode())
                            file_path = os.path.join(file_folder, file_name)
                            file_path = os.path.abspath(file_path)  # Get full path
                            print(file_path)
                        else:
                            file_path = message.body.decode()

                        transcribe_client = Transcriber(file_path, self.__pipe)
                        await asyncio.to_thread(transcribe_client.transcribe_file)

                        if queue.name in message.body.decode():
                            break
