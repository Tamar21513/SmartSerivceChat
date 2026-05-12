from transformers import DistilBertTokenizerFast

def load_tokenizer(model_path: str):
    return DistilBertTokenizerFast.from_pretrained(model_path, local_files_only=True)

def encode_pair(tokenizer, question: str, answer: str, max_len: int = 128):
    out = tokenizer(
        question,
        answer,
        add_special_tokens=True,
        truncation=True,
        max_length=max_len,
        padding="max_length",
        return_tensors="pt"
    )

    return {
        "input_ids": out["input_ids"],
        "attention_mask": out["attention_mask"]
    }