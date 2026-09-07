import torch
from transformers import DistilBertTokenizerFast
from RuntimeSettings import load_runtime_settings

settings = load_runtime_settings()


def load_tokenizer(model_path: str):
    return DistilBertTokenizerFast.from_pretrained(model_path, local_files_only=True)

def prepare_token_weights(token_weights, max_len: int = settings["max_len"]):
    if token_weights is None:
        token_weights = [1.0] * max_len
    else:
        # מוסיפים משקל רגיל עבור [CLS] שנוסף אוטומטית בתחילת הטקסט
        token_weights = [1.0] + token_weights

    if len(token_weights) > max_len:
        token_weights = token_weights[:max_len]

    if len(token_weights) < max_len:
        token_weights = token_weights + [1.0] * (max_len - len(token_weights))

    return torch.tensor([token_weights], dtype=torch.float)


def encode_pair(tokenizer, text: str, max_len: int = settings["max_len"], token_weights=None):
    out = tokenizer(
        text,
        add_special_tokens=True,
        truncation=True,
        max_length=max_len,
        padding="max_length",
        return_tensors="pt"
    )

    token_weights = prepare_token_weights(
        token_weights=token_weights,
        max_len=max_len
    )

    return {
        "input_ids": out["input_ids"],
        "attention_mask": out["attention_mask"],
        "token_weights": token_weights
    }