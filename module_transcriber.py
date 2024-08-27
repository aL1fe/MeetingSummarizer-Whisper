import time
import asyncio


class Transcriber:
    def __init__(self, file_path, pipe):
        self.__file_path = file_path
        self.__pipe = pipe

    async def transcribe_file(self):
        start_time = time.time()

        result = self.__pipe(self.__file_path)  # Transcribe file
        print(f"File was transcribed.")

        execution_time = round((time.time() - start_time), 2)

        # TODO save TranscribedRecord output_file_path = os.path.join(output_folder, f"{filename}.mp")

        return result, execution_time
