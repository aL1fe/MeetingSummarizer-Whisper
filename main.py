import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
import os
from dotenv import load_dotenv
from module_broker import BrokerClient


load_dotenv()
upload_folder = 'incoming_files'

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

pipe = pipeline(
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


# def main():
try:
    queue_name = "converted_files_queue"
    broker_client = BrokerClient(queue_name, pipe)
    broker_client.receive_message()
except Exception as e:
    print(f"Status: Error: {str(e)}")


if __name__ == "__main__":
    main()
