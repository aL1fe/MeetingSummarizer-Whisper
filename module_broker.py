import asyncio
import aio_pika
import aio_pika.abc
import os
from module_transcriber import Transcriber
from module_config import ConfigManager


class BrokerClient:
    def __init__(self, app_config, transcribe_client):
        self.__app_config = app_config
        self.__transcribe_client = transcribe_client

    async def __connect_to_broker(self):
        # Establishing a connection to RabbitMQ
        connection = await aio_pika.connect_robust(
            host=self.__app_config.broker_host,
            port=5672,
            virtualhost='/',
            login=self.__app_config.broker_login,
            password=self.__app_config.broker_password
        )
        return connection

    async def receive_message(self):
        connection = await self.__connect_to_broker()
        async with connection:
            queue_name = self.__app_config.converted_files_queue
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
                        if self.__app_config.broker_host == '127.0.0.1':
                            file_folder = self.__app_config.folder_with_converted_files
                            file_name = os.path.basename(message.body.decode())
                            file_path = os.path.join(file_folder, file_name)
                            file_path = os.path.abspath(file_path)  # Get full path
                        else:
                            file_path = message.body.decode()
                        print(file_path)

                        # await asyncio.to_thread(self.__transcribe_client.transcribe_file, file_path)
                        result, execution_time = await asyncio.create_task(
                            self.__transcribe_client.transcribe_file(file_path)
                        )
                        print(result["text"])
                        print(execution_time)

                        await self.publish_message(
                            connection,
                            self.__app_config.transcribed_files_queue,
                            result["text"]
                        )

                        if queue.name in message.body.decode():
                            break

    async def publish_message(self, connection, queue_name, message):
        channel: aio_pika.abc.AbstractChannel = await connection.channel()
        # Declare a queue
        queue: aio_pika.abc.AbstractQueue = await channel.declare_queue(
            queue_name,
            auto_delete=False,
            durable=True
        )
        await channel.default_exchange.publish(
            aio_pika.Message(
                body=message.encode('utf-8')
            ),
            routing_key=queue_name
        )
