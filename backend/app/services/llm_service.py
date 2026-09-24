import numpy as np
import onnxruntime as ort
from transformers import AutoTokenizer
import json
import re

MODEL_PATH = "models/SmolLM2-360M-Instruct/onnx/model_int8.onnx"
TOKENIZER_PATH = "models/SmolLM2-360M-Instruct"

#Converts human prompt into input_ids (numbers) and creates the attention_mask
tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_PATH)
#use onnx run time
session = ort.InferenceSession(MODEL_PATH)

def generate_text(prompt:str, max_new_tokens: int = 500) -> str:
    #Turns text prompt into NumPy arrays ready for ONNX Runtime.
    tokens = tokenizer(prompt, return_tensors = "np")

    input_ids = tokens["input_ids"].astype(np.int64)
    #It decide which token to pay attention which one to ignore.
    attention_mask = np.ones_like(input_ids, dtype=np.int64)

    #position_ids tells the model the exact word order so it knows which word
    #  came first, second, and third.
    position_ids = np.arange(
        input_ids.shape[1],
        dtype=np.int64
    ).reshape(1, -1)

    inputs = {
        "input_ids": input_ids,
        "attention_mask": attention_mask,
        "position_ids": position_ids,
    }

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

    next_token_id = np.argmax(outputs[0][0, -1])
    generated_ids = [next_token_id]

    prompt_length = input_ids.shape[1]

    for _ in range(max_new_tokens - 1):
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

    response = tokenizer.decode(
        generated_ids,
        skip_special_tokens=True,    
    )
    if "assistant" in response:
        response = response.split("assistant", 1)[1].strip()
    
    return response

DEFAULT_MEDICINE_SCHEMA = {
    "name": None,
    "dosage": None,
    "frequency": None,
    "duration": None,
    "instructions": None,
}

FORM_PREFIX_REGEX = re.compile(
    r"^(tablet|tab|capsule|cap|syrup|syp|inj|injection)\.?\s+",
    re.IGNORECASE,
)


def clean_medicine_dict(data: dict) -> dict:
    merged = {**DEFAULT_MEDICINE_SCHEMA, **data}
    if merged["name"]:
        merged["name"] = FORM_PREFIX_REGEX.sub("", merged["name"]).strip()
    return merged


def parse_medicines(medicine_lines: list[str]) -> list[dict]:
    medicines = []

    for medicine_text in medicine_lines:
        messages = [
            {
                "role": "system",
                "content": (
                    "Extract prescription details into JSON.\n"
                    "Always include all 5 keys: name, dosage, frequency, duration, instructions.\n"
                    "Rules:\n"
                    "- name: pure drug name only (exclude Tablet, Tab, Cap, etc.).\n"
                    "- Set missing fields explicitly to null.\n"
                    "- Output valid JSON only."
                ),
            },
            {
                "role": "user",
                "content": "Extract JSON for: Tablet Paracetamol 500 mg twice daily with water",
            },
            {
                "role": "assistant",
                "content": (
                    '{"name": "Paracetamol", "dosage": "500 mg", '
                    '"frequency": "twice daily", "duration": null, '
                    '"instructions": "with water"}'
                ),
            },
            {
                "role": "user",
                "content": f"Extract JSON for: {medicine_text}",
            },
        ]

        formatted_prompt = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )

        response = generate_text(formatted_prompt, max_new_tokens=200)

        json_start = response.find("{")
        json_end = response.rfind("}") + 1

        if json_start == -1 or json_end == 0:
            raise ValueError(f"LLM did not return JSON for: {medicine_text}")

        clean_json_str = response[json_start:json_end]
        raw_dict = json.loads(clean_json_str)
        medicines.append(clean_medicine_dict(raw_dict))

    return medicines