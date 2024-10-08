import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
import time


# Singleton pattern
class Transcriber:
    __instance = None
    __initialized = False

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self):
        if Transcriber.__initialized:
            return
        Transcriber.__initialized = True
        if torch.cuda.is_available():
            device = "cuda:0"
            print("CUDA is available. Using GPU.")
            print(f"Torch CUDA version {torch.version.cuda}")
        else:
            device = "cpu"
            print("CUDA is not available. Using CPU.")

        torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

        model_id = "openai/whisper-large-v3"

        model = AutoModelForSpeechSeq2Seq.from_pretrained(
            model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
        )
        model.to(device)

        processor = AutoProcessor.from_pretrained(model_id)

        self.__pipe = pipeline(
            "automatic-speech-recognition",
            model=model,
            tokenizer=processor.tokenizer,
            feature_extractor=processor.feature_extractor,
            max_new_tokens=128,
            chunk_length_s=25,
            batch_size=1,
            # return_timestamps=True,
            torch_dtype=torch_dtype,
            device=device,
            generate_kwargs={"language": "en", "suppress_tokens": []}
        )

    async def transcribe_file(self, file_path):
        start_time = time.time()

        result = self.__pipe(file_path)  # Transcribe file
        print(f"File was transcribed.")

        execution_time = round((time.time() - start_time), 2)

        return result, execution_time
