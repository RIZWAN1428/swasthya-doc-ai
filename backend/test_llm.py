import onnxruntime as ort
import numpy as np
from transformers import AutoTokenizer

MODEL_PATH = "models/SmolLM2-360M-Instruct/onnx/model_int8.onnx"
TOKENIZER_PATH = "models/SmolLM2-360M-Instruct"

tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_PATH)

session = ort.InferenceSession(MODEL_PATH)

text = "What is the capital of India?"
tokens = tokenizer(text, return_tensors="np")

input_ids = tokens["input_ids"].astype(np.int64)

attention_mask = np.ones_like(input_ids, dtype=np.int64)

position_ids = np.arange(
    input_ids.shape[1],
    dtype=np.int64
).reshape(1, -1)


inputs = {
    "input_ids": input_ids,
    "attention_mask": attention_mask,
    "position_ids": position_ids,
}


# Empty KV cache for the first pass
for i in range(32):
    inputs[f"past_key_values.{i}.key"] = np.zeros(
        (1, 5, 0, 64),
        dtype=np.float32
    )

    inputs[f"past_key_values.{i}.value"] = np.zeros(
        (1, 5, 0, 64),
        dtype=np.float32
    )


outputs = session.run(None, inputs)

logits = outputs[0]

next_token_id = np.argmax(logits[0, -1])
generated_ids = [next_token_id]

prompt_length = input_ids.shape[1]

for _ in range(30):
    past_length = prompt_length + len(generated_ids) - 1

    input_ids = np.array(
        [[generated_ids[-1]]],
        dtype=np.int64
    )

    attention_mask = np.ones(
        (1, past_length + 1),
        dtype=np.int64
    )

    position_ids = np.array(
        [[past_length]],
        dtype=np.int64
    )

    inputs = {
        "input_ids": input_ids,
        "attention_mask": attention_mask,
        "position_ids": position_ids,
    }

    for i in range(32):
        inputs[f"past_key_values.{i}.key"] = outputs[1 + i * 2]
        inputs[f"past_key_values.{i}.value"] = outputs[2 + i * 2]

    outputs = session.run(None, inputs)

    next_token_id = np.argmax(outputs[0][0, -1])
    if next_token_id == tokenizer.eos_token_id:
        break
    generated_ids.append(next_token_id)


#print("Generated IDs:", generated_ids)
print("Generated text:", tokenizer.decode(generated_ids))