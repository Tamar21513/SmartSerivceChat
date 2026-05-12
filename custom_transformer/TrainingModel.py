import torch
import torch.nn as nn
from transformers import get_scheduler
from my_tokenize import load_tokenizer, encode_pair
from preprocess import my_split
from torch import optim
from torch.utils.data import DataLoader
import csv
import os

from qa_matching_model import QAMatchingTransformer


device = "cpu"
num_epochs = 20
learning_rate = 5e-5
batch_size = 8
max_len = 128


tokenizer = load_tokenizer(
    r"C:\Tamarush\programming\project\ChatTM\Felis_python\models\distilbert-base-cased-distilled-squad"
)


model = QAMatchingTransformer(
    hidden_dim=128,
    vocab_size=tokenizer.vocab_size,
    max_position_embeddings=128,
    num_heads=4,
    num_blocks=2,
    num_labels=1
)


encoded_dataset = []

csv_path = r"C:\Tamarush\programming\project\ChatTM\Felis_python\data\qa_matching_dataset.csv"

with open(csv_path, mode="r", encoding="utf-8") as file:
    reader = csv.DictReader(file)

    for row in reader:
        question = row["question"]
        answer = row["answer"]
        score = float(row["score"])

        cleaned_question = my_split(question)
        cleaned_answer = my_split(answer)

        encoded = encode_pair(
            tokenizer,
            cleaned_question,
            cleaned_answer,
            max_len=max_len
        )

        encoded["input_ids"] = encoded["input_ids"].squeeze(0)
        encoded["attention_mask"] = encoded["attention_mask"].squeeze(0)
        encoded["labels"] = torch.tensor([score], dtype=torch.float)

        encoded_dataset.append(encoded)


train_dataloader = DataLoader(
    encoded_dataset,
    batch_size=batch_size,
    shuffle=True
)


model.to(device)

optimizer = optim.AdamW(
    model.parameters(),
    lr=learning_rate
)

num_training_steps = num_epochs * len(train_dataloader)

lr_scheduler = get_scheduler(
    "linear",
    optimizer=optimizer,
    num_warmup_steps=0,
    num_training_steps=num_training_steps
)

criterion = nn.BCEWithLogitsLoss()

model.train()

for epoch in range(num_epochs):
    print(f"\n--- Starting Epoch {epoch + 1}/{num_epochs} ---")

    total_loss = 0

    for batch in train_dataloader:
        input_ids = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)
        labels = batch["labels"].to(device)

        logits = model(input_ids, attention_mask)

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


def test_model(model, tokenizer, question, answer, device="cpu"):
    model.to(device)
    model.eval()

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

    print("\n--- Test Prediction ---")
    print(f"Question: {question}")
    print(f"Answer: {answer}")
    print(f"Match score: {score.item():.4f}")

test_model(
    model,
    tokenizer,
    "How much does it cost to ship a wireless mouse from Tel Aviv to Jerusalem with ExpressShip in two days for 1 units?",
    "Shipping a wireless mouse from Tel Aviv to Jerusalem with ExpressShip costs $12 for 1 units and may change during holidays.",
    device=device
)

test_model(
    model,
    tokenizer,
    "How can I reset my password?",
    "Your order will arrive tomorrow.",
    device=device
)