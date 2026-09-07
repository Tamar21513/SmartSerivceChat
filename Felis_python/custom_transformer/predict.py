import torch
import os


from custom_transformer.my_tokenize import load_tokenizer, encode_pair
from custom_transformer.preprocess import my_split
from custom_transformer.qa_matching_model import QAMatchingTransformer
from RuntimeSettings import load_runtime_settings

settings = load_runtime_settings()



device = "cpu"


BASE_DIR = r"C:\Tamarush\programming\project\ChatTM\Felis_python"

TOKENIZER_DIR = os.path.join(BASE_DIR, "models", "distilbert-base-cased-distilled-squad")
MODEL_DIR = os.path.join(BASE_DIR, "models", "qa_matching_model")
MODEL_WEIGHTS_PATH = os.path.join(MODEL_DIR, "qa_matching_model_weights.pt")


tokenizer = load_tokenizer(TOKENIZER_DIR)

model = QAMatchingTransformer(
    hidden_dim=settings["hidden_dim"],
    vocab_size=tokenizer.vocab_size,
    max_position_embeddings=settings["max_position_embeddings"],
    num_heads=settings["num_heads_to_predict"],
    num_blocks=settings["num_blocks"],
    num_labels=settings["num_labels"]
)

model.load_state_dict(
    torch.load(MODEL_WEIGHTS_PATH, map_location=device)
)

model.to(device)
model.eval()

# Predict the match score between a question and an answer using the trained QA matching model
def predict_match(text: str, token_weights=None) -> float:
    cleaned_text = my_split(text)
    encoded = encode_pair(tokenizer, cleaned_text, max_len=settings["max_len"], token_weights=token_weights)
    input_ids = encoded["input_ids"].to(device)
    attention_mask = encoded["attention_mask"].to(device)
    token_weights = encoded["token_weights"].to(device)
    with torch.no_grad():
        score = model(
            input_ids,
            attention_mask,
            token_weights=token_weights,
            return_score=True
        )
    return score.item()


if __name__ == "__main__":
    text = (
        "topic: pricing , "
        "question: How much does it cost to fly from Israel to Greece with El Al in April for one person? , "
        "answer: A flight from Israel to Greece with El Al in April for one person starts at $72 for a one-way ticket and $101 for a round-trip ticket."
    )

    token_weights = [
        0.2, 3.0, 1.0, 1.0,
        1.0, 1.0, 2.5, 2.5,
        1.0, 1.5, 1.0, 1.5,
        1.0, 3.0, 3.0,
        1.0, 1.0, 1.0, 1.0, 1.0
    ]
    score = predict_match(
        text,
        token_weights=token_weights
    )

    print("Text:", text)
    print(f"Match score: {score:.4f}")