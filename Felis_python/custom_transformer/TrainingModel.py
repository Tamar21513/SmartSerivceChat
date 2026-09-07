import torch
import torch.nn as nn
from transformers import get_scheduler
from custom_transformer.my_tokenize import load_tokenizer, encode_pair
from custom_transformer.preprocess import my_split
from torch import optim
from torch.utils.data import DataLoader
import csv
import os
from custom_transformer.qa_matching_model import QAMatchingTransformer
from RuntimeSettings import load_runtime_settings

settings = load_runtime_settings()









tokenizer = load_tokenizer(
    r"C:\Tamarush\programming\project\ChatTM\Felis_python\models\distilbert-base-cased-distilled-squad"
)


model = QAMatchingTransformer(
    hidden_dim=settings["hidden_dim"],
    vocab_size=tokenizer.vocab_size,
    max_position_embeddings=settings["max_position_embeddings"],
    num_heads=settings["num_heads_to_predict"],
    num_blocks=settings["num_blocks"],
    num_labels=settings["num_labels"]
)


# Parse a comma-separated token_weights string from a CSV row into a list of floats
def parse_token_weights(row):
    weights_text = row.get("token_weights", "")

    if weights_text is None or weights_text.strip() == "":
        return None

    return [float(x.strip()) for x in weights_text.split(",") if x.strip() != ""]


encoded_dataset = []

csv_path = r"C:\Tamarush\programming\project\ChatTM\Felis_python\data\qa_matching_dataset.csv"

with open(csv_path, mode="r", encoding="utf-8") as file:
    reader = csv.DictReader(file)

    for row in reader:
        topic = row["topic"]
        question = row["question"]
        answer = row["answer"]
        score = float(row["score"])

        cleaned_question = my_split(question)
        cleaned_answer = my_split(answer)

        full_text = "topic: " + topic + " , question: " + cleaned_question + " , answer: " + cleaned_answer

        token_weights = parse_token_weights(row)

        encoded = encode_pair(
            tokenizer,
            full_text,
            max_len=settings["max_len"],
            token_weights=token_weights
        )

        encoded["input_ids"] = encoded["input_ids"].squeeze(0)
        encoded["attention_mask"] = encoded["attention_mask"].squeeze(0)
        encoded["token_weights"] = encoded["token_weights"].squeeze(0)
        encoded["labels"] = torch.tensor([score], dtype=torch.float)

        encoded_dataset.append(encoded)


train_dataloader = DataLoader(
    encoded_dataset,
    batch_size=settings["batch_size"],
    shuffle=True
)


model.to(settings["device"])

optimizer = optim.AdamW(
    model.parameters(),
    lr=settings["learning_rate"]
)

num_training_steps = settings["num_epochs"] * len(train_dataloader)

lr_scheduler = get_scheduler(
    "linear",
    optimizer=optimizer,
    num_warmup_steps=0,
    num_training_steps=num_training_steps
)

criterion = nn.BCEWithLogitsLoss()

model.train()

for epoch in range(settings["num_epochs"]):
    print(f"\n--- Starting Epoch {epoch + 1}/{settings["num_epochs"]} ---")

    total_loss = 0

    for batch in train_dataloader:
        input_ids = batch["input_ids"].to(settings["device"])
        attention_mask = batch["attention_mask"].to(settings["device"])
        token_weights = batch["token_weights"].to(settings["device"])
        labels = batch["labels"].to(settings["device"])

        logits = model(
            input_ids,
            attention_mask,
            token_weights=token_weights
        )

        loss = criterion(logits, labels)

        loss.backward()
        optimizer.step()
        lr_scheduler.step()
        optimizer.zero_grad()

        total_loss += loss.item()

    avg_loss = total_loss / len(train_dataloader)
    print(f"Epoch {epoch + 1} average loss: {avg_loss:.4f}")


print("\nTraining finished! Saving model weights...")

save_dir = r"C:\Tamarush\programming\project\ChatTM\Felis_python\models\qa_matching_model"
os.makedirs(save_dir, exist_ok=True)

torch.save(model.state_dict(), os.path.join(save_dir, "qa_matching_model_weights.pt"))

#tokenizer.save_pretrained(save_dir)

print(f"Model weights saved to {save_dir}")
print(f"Tokenizer saved to {save_dir}")


# Run the model on a single topic/question/answer example and print its predicted match score
def test_model(model, tokenizer, topic, question, answer, token_weights=None, device="cpu"):
    model.to(device)
    model.eval()

    cleaned_question = my_split(question)
    cleaned_answer = my_split(answer)

    full_text = "topic: " + topic + " , question: " + cleaned_question + " , answer: " + cleaned_answer

    encoded = encode_pair(
        tokenizer,
        full_text,
        max_len=settings["max_len"],
        token_weights=token_weights
    )

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

    print("\n--- Test Prediction ---")
    print(f"Topic: {topic}")
    print(f"Question: {question}")
    print(f"Answer: {answer}")
    print(f"Match score: {score.item():.4f}")


test_model(
    model,
    tokenizer,
    "pricing",
    "How much does it cost to fly from Israel to Greece with El Al in April for one person?",
    "Check out these great prices for the next 90 days, starting at just $72 for a one-way ticket and $101 for a round-trip.",
    token_weights=[0.2, 3.0, 1.0, 1.0, 1.0, 1.0, 2.5, 2.5, 1.0, 1.5, 1.0, 1.5, 1.0, 3.0, 3.0, 1.0, 1.0, 1.0, 1.0, 1.0],
    device=settings["device"]
)

test_model(
    model,
    tokenizer,
    "pricing",
    "How can I reset my password?",
    "Your order will arrive tomorrow.",
    token_weights=None,
    device=settings["device"]
)