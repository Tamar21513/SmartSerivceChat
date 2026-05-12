import torch
import os


from custom_transformer.my_tokenize import load_tokenizer, encode_pair
from custom_transformer.preprocess import my_split
from custom_transformer.qa_matching_model import QAMatchingTransformer


device = "cpu"
max_len = 128

BASE_DIR = r"C:\Tamarush\programming\project\ChatTM\Felis_python"

TOKENIZER_DIR = os.path.join(BASE_DIR, "models", "distilbert-base-cased-distilled-squad")
MODEL_DIR = os.path.join(BASE_DIR, "models", "qa_matching_model")
MODEL_WEIGHTS_PATH = os.path.join(MODEL_DIR, "qa_matching_model_weights.pt")


tokenizer = load_tokenizer(TOKENIZER_DIR)

model = QAMatchingTransformer(
    hidden_dim=128,
    vocab_size=tokenizer.vocab_size,
    max_position_embeddings=128,
    num_heads=4,
    num_blocks=2,
    num_labels=1
)

model.load_state_dict(
    torch.load(MODEL_WEIGHTS_PATH, map_location=device)
)

model.to(device)
model.eval()


def predict_match(question: str, answer: str) -> float:
    cleaned_question = my_split(question)
    cleaned_answer = my_split(answer)

    encoded = encode_pair(
        tokenizer,
        cleaned_question,
        cleaned_answer,
        max_len=max_len
    )

    input_ids = encoded["input_ids"].to(device)
    attention_mask = encoded["attention_mask"].to(device)

    with torch.no_grad():
        score = model(
            input_ids,
            attention_mask,
            return_score=True
        )

    return score.item()


if __name__ == "__main__":
    question = "How much does it cost to ship a wireless mouse from Tel Aviv to Jerusalem with ExpressShip in two days for 1 units?"
    answer = "Shipping a wireless mouse from Tel Aviv to Jerusalem with ExpressShip costs $12 for 1 units and may change during holidays."

    score = predict_match(question, answer)

    print("Question:", question)
    print("Answer:", answer)
    print(f"Match score: {score:.4f}")