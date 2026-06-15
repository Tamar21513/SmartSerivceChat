import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from ModelManager import flan_t5_tokenizer, flan_t5_model
from RuntimeSettings import load_runtime_settings

settings = load_runtime_settings()


tokenizer = flan_t5_tokenizer
model = flan_t5_model


model.eval()

#פונקציה המאחדת משקל - למילה
def build_weighted_tokens(question, weights):
    words = question
    print("words")
    print(words)

    if len(words) != len(weights):
        print("Warning: number of words and weights is not equal")
        min_len = min(len(words), len(weights))
        words = words[:min_len]
        weights = weights[:min_len]

    weighted_tokens = []

    for word, weight in zip(words, weights):
        weighted_tokens.append(f"{word}={weight}")

    return ", ".join(weighted_tokens)


#בנית תשובה
def create_answer(question, context, topic, weights=None):
    weighted_tokens = build_weighted_tokens(question, weights[4:])

    prompt = f"""
You are a customer support assistant.

Use only the provided context snippets.
Do not invent information.
Do not add products, prices, dates, or details that are not written in the context.
If several options appear in the context, list each option on a separate line.
For pricing questions, show the cheapest option if it can be identified.
The ending question must be directly about the same product or same options in the answer.
The ending question must not ask for information that was already answered.
The ending question should offer a useful next step about the same item.
For pricing questions, ask if the user wants a comparison, availability, or features of the listed options.

Return exactly this format:
answer: ...
ending: ...

Topic: {topic}

Question:
{question}

Weighted question tokens:
{weighted_tokens}

Context snippets:
{context}
"""

    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        max_length=512,
        truncation=True
    ).to(model.device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=160,
            do_sample=False,
            num_beams=4,
            no_repeat_ngram_size=3,
            repetition_penalty=1.2
        )
    print("RAW OUTPUT IDS:")
    print(outputs[0].tolist())

    print("DECODE WITH SPECIAL TOKENS:")
    print(tokenizer.decode(outputs[0], skip_special_tokens=False))

    print("DECODE WITHOUT SPECIAL TOKENS:")
    print(tokenizer.decode(outputs[0], skip_special_tokens=True))
    return tokenizer.decode(outputs[0], skip_special_tokens=True)



#לא נראה לי שצריך--------------------
def get_general_topic(topic, question, contexts, weighted_tokens):
    prompt = f"""
You are a customer support assistant.

Use only the provided context snippets.
The question is already cleaned and shortened.
Pay more attention to tokens with higher weights.
Do not invent missing information.
If the context does not contain enough information, say that clearly.
Write naturally and personally, but stay professional.
Return exactly this format:

answer: ...
ending: ...

Topic:
{topic}

Question:
{question}

Weighted question tokens:
{weighted_tokens}

Context snippets:
{contexts}
"""
    inputs = tokenizer(prompt, return_tensors="pt",truncation=True)
    outputs = model.generate(**inputs,max_new_tokens=90,do_sample=False,num_beams=4,early_stopping=True,no_repeat_ngram_size=3,repetition_penalty=1.2)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)





import json
import torch

DATA_FILE = r"C:\Tamarush\programming\project\ChatTM\Felis_python\data\flan_t5_large_dataset_with_complaints.jsonl"

with open(DATA_FILE, "r", encoding="utf-8") as f:
    for line in f:
        item = json.loads(line)
        if str(item.get("output", "")).strip():
            prompt = item["input"]
            expected = item["output"]
            break

print("EXPECTED:")
print(expected)

inputs = tokenizer(
    prompt,
    return_tensors="pt",
    max_length=512,
    truncation=True
).to(model.device)

with torch.no_grad():
    outputs = model.generate(
        **inputs,
        max_new_tokens=120,
        min_new_tokens=20,
        do_sample=False,
        num_beams=1,
        eos_token_id=tokenizer.eos_token_id,
        pad_token_id=tokenizer.pad_token_id
    )

print("RAW:", outputs[0].tolist())
print("TEXT WITH SPECIAL:", tokenizer.decode(outputs[0], skip_special_tokens=False))
print("TEXT:", tokenizer.decode(outputs[0], skip_special_tokens=True))


#------------------------בדיקה אם עובד------------------

#q = "I have a really good camera and I want to know how to take good pictures."
#
#c= """
#To take good pictures, you should learn how your camera works, try different angles,
#pay attention to sharpness, use good light, and practice often.
#Every image will not be perfect, and improvement comes through trial and error.
#"""
#
#q="How much does a flight to Greece cost in April for one person?"
#
#c="""
#-----------paragraphs to answer-------------
#Greece Flights as Low as $106. These prices were available within the past 7 days. Prices quoted are per person, round trip, for the period specified. Prices and availability are subject to change. Additional terms apply.
#
# Sep 8 - Thu, Sep 10. ATH. Eleftherios Venizelos. HER. Nikos Kazantzakis $117 Roundtrip, found 2 hours ago $117. Roundtrip found 2 hours ago. Sun, May 31 - Mon, Jun 8. ATH. Eleftherios Venizelos. SKG. Macedonia $119 Roundtrip, found 1 hour ago $119. Roundtrip found 1 hour ago. Tue, Sep 8 - Thu, Sep 10. ATH. Eleftherios Venizelos. HER. Nikos Kazantzakis $121 Roundtrip, found 2 hours ago $121. Roundtrip found 2 hours ago. Sat, Jun 27 - Tue, Jun 30. ATH. Eleftherios Venizelos. CHQ. Ioannis Daskalogiannis $161 Roundtrip, found 2 days ago $161. Roundtrip found 2 days ago. Greece Flights. For seniors in search of the best deals on airfares, AARP Travel Center Powered by Expedia features low-cost flights in Greece. Right here you may enter your expected travel dates
#
# Tue, Sep 8 - Thu, Sep 10. ATH. Eleftherios Venizelos. HER. Nikos Kazantzakis $106 Roundtrip, found 2 hours ago $106. Roundtrip found 2 hours ago. Sun, May 31 - Mon, Jun 8. ATH. Eleftherios Venizelos. SKG. Macedonia $109 Roundtrip, found 1 hour ago $109. Roundtrip found 1 hour ago. Tue, Sep 8 - Thu, Sep 10. ATH. Eleftherios Venizelos. HER. Nikos Kazantzakis $111 Roundtrip, found 2 hours ago $111. Roundtrip found 2 hours ago. Tue, Sep 8 - Thu, Sep 10. ATH. Eleftherios Venizelos. HER. Nikos Kazantzakis $114 Roundtrip, found 2 hours ago $114. Roundtrip found 2 hours ago. Tue, Sep 8 - Thu, Sep 10. ATH. Eleftherios Venizelos. HER. Nikos Kazantzakis $117 Roundtrip, found 2 hours ago $117. Roundtrip found 2 hours ago. Sun, May 31 - Mon, Jun,
#
# For seniors in search of the best deals on airfares, AARP Travel Center Powered by Expedia features low-cost flights in Greece. Right here you may enter your expected travel dates to browse through the selection of cheap flights for seniors in Greece. The search engine presents a variety of low-cost plane tickets, airline carriers, and travel times to ensure the Greece AARP Travel Center flights suit your travel needs and preferences. And on top of affordable airline tickets, AARP members also enjoy no additional booking fees when you book your Greece senior flights on AARP Travel Center Powered by Expedia. These senior flights to or from Greece allow you to jet set without breaking the bank.
#"""
#answer = create_answer(q,c)
#print()
#print()
#print()
#print("---------------the answer--------------")
#print(answer)






#----------------------------אימון מודל שכתבתי לבד בסד--------------
#import os
#import gc
#import json
#import torch
#import numpy as np
#import nltk
#import evaluate
#
#from datasets import load_dataset
#from transformers import (
#    AutoTokenizer,
#    AutoModelForSeq2SeqLM,
#    DataCollatorForSeq2Seq,
#    Seq2SeqTrainingArguments,
#    Seq2SeqTrainer,
#)
#
#
## =========================
## Paths
## =========================
#
#BASE_DIR = r"C:\Tamarush\programming\project\ChatTM\Felis_python"
#
#DATA_FILE = os.path.join(BASE_DIR,"data" ,"flan_t5_large_dataset_with_complaints.jsonl")
#
#
#MODEL_NAME = os.path.join(BASE_DIR, "models", "flan-t5-large")
#
#
#OUTPUT_DIR = os.path.join(BASE_DIR, "models", "trained_flan_t5_large_local")
#RESULTS_DIR = os.path.join(BASE_DIR, "results_flan_t5_large_local")
#
#
## =========================
## Safety / device
## =========================
#
#gc.collect()
#
#if torch.cuda.is_available():
#    torch.cuda.empty_cache()
#    DEVICE = "cuda"
#else:
#    DEVICE = "cpu"
#
#print("Device:", DEVICE)
#
#if DEVICE == "cpu":
#    print("WARNING: Training FLAN-T5-LARGE on CPU will be very slow.")
#
#
## =========================
## Load tokenizer + model
## =========================
#
#print("Loading tokenizer...")
#
#tokenizer = AutoTokenizer.from_pretrained(
#    MODEL_NAME,
#    use_fast=True
#)
#
#print("Loading model...")
#
#model = AutoModelForSeq2SeqLM.from_pretrained(
#    MODEL_NAME,
#    torch_dtype=torch.float32,
#    low_cpu_mem_usage=True
#)
#
#model.to(DEVICE)
#model.config.use_cache = False
#model.train()
#
#print("Model loaded")
#print("Model dtype:", next(model.parameters()).dtype)
#
#
## =========================
## Load dataset
## =========================
#
#if not os.path.exists(DATA_FILE):
#    raise FileNotFoundError(f"Dataset file not found: {DATA_FILE}")
#
#raw_dataset = load_dataset(
#    "json",
#    data_files=DATA_FILE
#)["train"]
#
#print("Raw dataset:", raw_dataset)
#print("First example:", raw_dataset[0])
#
#
## =========================
## Clean dataset
## =========================
#
#def clean_example(example):
#    topic = str(example.get("topic", "")).strip()
#    input_text = str(example.get("input", "")).strip()
#    output_text = str(example.get("output", "")).strip()
#
#    return {
#        "topic": topic,
#        "input": input_text,
#        "output": output_text
#    }
#
#
#dataset = raw_dataset.map(clean_example)
#
#dataset = dataset.filter(
#    lambda x: len(x["input"]) > 0 and len(x["output"]) > 0
#)
#
#print("Dataset after cleaning:", len(dataset))
#
#
#split_dataset = dataset.train_test_split(
#    test_size=0.1,
#    seed=42
#)
#
#train_dataset = split_dataset["train"]
#eval_dataset = split_dataset["test"]
#
#print("Train:", len(train_dataset))
#print("Eval:", len(eval_dataset))
#
#print("\nSample input:")
#print(train_dataset[0]["input"])
#print("\nSample output:")
#print(train_dataset[0]["output"])
#
#
## =========================
## Tokenize
## =========================
#
#MAX_INPUT_LENGTH = 384
#MAX_TARGET_LENGTH = 96
#
#
#def preprocess_function(examples):
#    inputs = []
#    targets = []
#
#    for inp, out in zip(examples["input"], examples["output"]):
#        inp = "" if inp is None else str(inp).strip()
#        out = "" if out is None else str(out).strip()
#
#        inputs.append(inp)
#        targets.append(out)
#
#    model_inputs = tokenizer(
#        inputs,
#        max_length=MAX_INPUT_LENGTH,
#        truncation=True,
#        padding="max_length"
#    )
#
#    labels = tokenizer(
#        text_target=targets,
#        max_length=MAX_TARGET_LENGTH,
#        truncation=True,
#        padding="max_length"
#    )
#
#    labels_ids = labels["input_ids"]
#
#    # קריטי: לא לתת למודל ללמוד padding
#    labels_ids = [
#        [
#            token if token != tokenizer.pad_token_id else -100
#            for token in label
#        ]
#        for label in labels_ids
#    ]
#
#    model_inputs["labels"] = labels_ids
#
#    return model_inputs
#
#
#tokenized_dataset = split_dataset.map(
#    preprocess_function,
#    batched=True,
#    remove_columns=split_dataset["train"].column_names
#)
#
#tokenized_train = tokenized_dataset["train"]
#tokenized_eval = tokenized_dataset["test"]
#
#
## =========================
## Check labels before training
## =========================
#
#example = tokenized_train[0]
#labels = example["labels"]
#
#num_real_labels = sum(1 for x in labels if x != -100)
#num_ignored_labels = sum(1 for x in labels if x == -100)
#
#decoded_labels = tokenizer.decode(
#    [x for x in labels if x != -100],
#    skip_special_tokens=True
#)
#
#print("\nLabel check:")
#print("Real labels:", num_real_labels)
#print("Ignored labels:", num_ignored_labels)
#print("Decoded labels:")
#print(decoded_labels)
#
#if num_real_labels == 0:
#    raise ValueError("All labels are -100. Training cannot continue.")
#
#
## =========================
## Data collator
## =========================
#
#data_collator = DataCollatorForSeq2Seq(
#    tokenizer=tokenizer,
#    model=model,
#    label_pad_token_id=-100
#)
#
#
## =========================
## Manual loss check
## =========================
#
#batch = {
#    "input_ids": torch.tensor([tokenized_train[0]["input_ids"]], dtype=torch.long).to(DEVICE),
#    "attention_mask": torch.tensor([tokenized_train[0]["attention_mask"]], dtype=torch.long).to(DEVICE),
#    "labels": torch.tensor([tokenized_train[0]["labels"]], dtype=torch.long).to(DEVICE),
#}
#
#with torch.no_grad():
#    outputs = model(**batch)
#
#manual_loss = outputs.loss.item()
#
#print("\nManual loss:", manual_loss)
#
#if np.isnan(manual_loss):
#    raise ValueError("Manual loss is NaN. Stop training.")
#
#if manual_loss == 0:
#    print("WARNING: Manual loss is 0. Check dataset and labels.")
#
#
## =========================
## Metrics
## =========================
#
#nltk.download("punkt", quiet=True)
#metric = evaluate.load("rouge")
#
#
#def compute_metrics(eval_preds):
#    preds, labels = eval_preds
#
#    if isinstance(preds, tuple):
#        preds = preds[0]
#
#    labels = np.where(labels != -100, labels, tokenizer.pad_token_id)
#
#    decoded_preds = tokenizer.batch_decode(
#        preds,
#        skip_special_tokens=True
#    )
#
#    decoded_labels = tokenizer.batch_decode(
#        labels,
#        skip_special_tokens=True
#    )
#
#    decoded_preds = [pred.strip() for pred in decoded_preds]
#    decoded_labels = [label.strip() for label in decoded_labels]
#
#    result = metric.compute(
#        predictions=decoded_preds,
#        references=decoded_labels,
#        use_stemmer=True
#    )
#
#    result["quality_percent"] = result["rougeL"] * 100
#
#    return result
#
#
## =========================
## Training args
## =========================
#
#training_args = Seq2SeqTrainingArguments(
#    output_dir=RESULTS_DIR,
#
#    learning_rate=5e-6,
#    num_train_epochs=1,
#
#    per_device_train_batch_size=1,
#    per_device_eval_batch_size=1,
#    gradient_accumulation_steps=16,
#
#    weight_decay=0.01,
#    max_grad_norm=1.0,
#
#    eval_strategy="epoch",
#    save_strategy="epoch",
#
#    logging_strategy="steps",
#    logging_steps=10,
#
#    # בזמן אימון מקומי זה חוסך זיכרון.
#    # אחרי אימון נעשה בדיקה ידנית עם generate.
#    predict_with_generate=False,
#
#    fp16=False,
#    bf16=False,
#
#    optim="adamw_torch",
#
#    save_total_limit=2,
#    report_to="none",
#    dataloader_pin_memory=False,
#    remove_unused_columns=False
#)
#
#
## =========================
## Trainer
## =========================
#
#trainer = Seq2SeqTrainer(
#    model=model,
#    args=training_args,
#    train_dataset=tokenized_train,
#    eval_dataset=tokenized_eval,
#    data_collator=data_collator,
#    processing_class=tokenizer
#)
#
#
## =========================
## Train
## =========================
#
#print("\nStarting training...")
#
#train_result = trainer.train()
#
#print("\nTrain result:")
#print(train_result)
#
#
## =========================
## Evaluate loss
## =========================
#
#eval_results = trainer.evaluate()
#
#print("\nEval results:")
#print(eval_results)
#
#
## =========================
## Save model
## =========================
#
#print("\nSaving model...")
#
#trainer.save_model(OUTPUT_DIR)
#tokenizer.save_pretrained(OUTPUT_DIR)
#
#print("Saved to:", OUTPUT_DIR)
#
#
## =========================
## Fix tokenizer_config.json
## =========================
#
#tokenizer_config_path = os.path.join(OUTPUT_DIR, "tokenizer_config.json")
#
#if os.path.exists(tokenizer_config_path):
#    with open(tokenizer_config_path, "r", encoding="utf-8") as f:
#        data = json.load(f)
#
#    changed = False
#
#    for key in ["extra_special_tokens", "tokenizer_class", "is_local", "local_files_only"]:
#        if key in data:
#            del data[key]
#            changed = True
#            print("Removed from tokenizer_config:", key)
#
#    with open(tokenizer_config_path, "w", encoding="utf-8") as f:
#        json.dump(data, f, ensure_ascii=False, indent=2)
#
#    print("tokenizer_config fixed:", changed)
#
#
## =========================
## Generation test
## =========================
#
#print("\nTesting generation...")
#
#model.eval()
#
#prompt = """
#You are a customer support assistant.
#Use only the provided context snippets.
#Return exactly this format:
#answer: ...
#ending: ...
#
#Topic: complaint
#Question: I want to complain about late delivery with my order reference 45872.
#Weighted question tokens: late delivery=3.0, order=2.5, reference 45872=2.0
#Context snippets:
#1. Complaints should be handled with empathy and professional language.
#2. Support may ask for missing details such as target or reference number.
#3. Improvement suggestions can help the company understand the customer experience.
#"""
#
#inputs = tokenizer(
#    prompt,
#    return_tensors="pt",
#    truncation=True,
#    max_length=MAX_INPUT_LENGTH
#).to(DEVICE)
#
#with torch.no_grad():
#    generated = model.generate(
#        **inputs,
#        max_new_tokens=100,
#        do_sample=False,
#        num_beams=4,
#        no_repeat_ngram_size=3,
#        repetition_penalty=1.8,
#        early_stopping=True,
#        eos_token_id=tokenizer.eos_token_id,
#        pad_token_id=tokenizer.pad_token_id
#    )
#
#answer = tokenizer.decode(
#    generated[0],
#    skip_special_tokens=True
#)
#
#print("\nGenerated answer:")
#print(answer)