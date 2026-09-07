import torch
from ModelManager import flan_t5_tokenizer, flan_t5_model
from RuntimeSettings import load_runtime_settings

settings = load_runtime_settings()

tokenizer = flan_t5_tokenizer
model = flan_t5_model

model.eval()


prefix = """
You are a customer support answer builder.

Input fields:
topic, question, content.

Task:
Write a customer support response.

Output format:
answer: ...
ending: ...

Rules:
- Use only the question and content.
- Do not invent facts, prices, dates, order status, policies, or product details.
- If exact information is missing, say it is not provided in the available context.
- For complaint topic, content may be empty.
- Do not copy instructions into the response.
- Always include both answer and ending.
"""

#תיקון סיומת התשובה
def fix_answer_format(text):
    text = str(text).strip()

    bad_sentences = [
        "The ending is yes.",
        "The ending is no.",
        "The ending is:",
        "The answer is:",
    ]

    for sentence in bad_sentences:
        text = text.replace(sentence, "").strip()

    lower = text.lower()

    if "answer:" not in lower:
        text = "answer: " + text
        lower = text.lower()

    if "ending:" not in lower:
        text += "\nending: Would you like me to help with the next step?"

    return text


def clean_model_output(text):
    text = str(text).strip()

    bad_phrases = [
        "Do not promise refund, compensation, replacement, repair, or escalation unless explicitly provided.",
        "The ending should ask for one useful next detail, such as reference number, affected product/service, or expected improvement.",
        "Then mention only the closest relevant prices from the content.",
        "If it is clear from the question, answer with that time.",
        "Do not invent facts, prices, dates, order status, policies, or product details.",
        "Return only valid JSON.",
        "Use only information that is available in the provided input.",
    ]

    for phrase in bad_phrases:
        text = text.replace(phrase, "").strip()

    return fix_answer_format(text)


# בניית תשובה סופית
def create_answer(question, context, topic):
    question = str(question).strip()
    context = str(context).strip()
    topic = str(topic).strip()

    # לפי האימון שלך: complaint בלי content
    if topic == "complaint":
        context = ""

    prompt = f"""
{prefix}

topic:
{topic}

question:
{question}

content:
{context}
"""

    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        max_length=768,
        truncation=True
    ).to(model.device)

    model.eval()

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=160,
            min_new_tokens=10,
            do_sample=False,
            num_beams=4,
            no_repeat_ngram_size=3,
            repetition_penalty=1.3,
            eos_token_id=tokenizer.eos_token_id,
            pad_token_id=tokenizer.pad_token_id
        )

    answer = tokenizer.decode(
        outputs[0],
        skip_special_tokens=True
    ).strip()

    print("RAW OUTPUT IDS:")
    print(outputs[0].tolist())

    print("DECODE WITHOUT SPECIAL TOKENS:")
    print(answer)

    answer = clean_model_output(answer)

    print("FINAL CLEAN ANSWER:")
    print(answer)

    return answer


##לא נראה לי שצריך--------------------
#def get_general_topic(topic, question, contexts, weighted_tokens):
#    prompt = f"""
#You are a customer support assistant.
#
#Use only the provided context snippets.
#The question is already cleaned and shortened.
#Pay more attention to tokens with higher weights.
#Do not invent missing information.
#If the context does not contain enough information, say that clearly.
#Write naturally and personally, but stay professional.
#Return exactly this format:
#
#answer: ...
#ending: ...
#
#Topic:
#{topic}
#
#Question:
#{question}
#
#Weighted question tokens:
#{weighted_tokens}
#
#Context snippets:
#{contexts}
#"""
#    inputs = tokenizer(prompt, return_tensors="pt",truncation=True)
#    outputs = model.generate(**inputs,max_new_tokens=90,do_sample=False,num_beams=4,early_stopping=True,no_repeat_ngram_size=3,repetition_penalty=1.2)
#    return tokenizer.decode(outputs[0], skip_special_tokens=True)
#
#




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
#----------------------------אימון מודל שכתבתי לבד בסד--------------





#
#prefix = """
#You are a professional customer support answer builder.
#
#Your task is to create a clear, accurate, and helpful customer service answer.
#
#You will receive:
#- topic: the topic/category of the customer request.
#- question: the cleaned and shortened customer question.
#- weights: importance weights for every word in the question.
#- content: context snippets retrieved from company data, database, or web search.
#  For topic = complaint, content may be empty and must not be required.
#
#GENERAL RULES:
#1. Use only information that is available in the provided input.
#2. Do not invent facts, prices, dates, times, policies, order status, product details, or company actions.
#3. Do not assume missing details.
#4. Do not mention information that is not supported by the question or content.
#5. If topic is complaint, content may be empty. Build the answer from the question and weights.
#6. If topic is not complaint, answer only from the content.
#7. If the exact requested information does not appear, say that clearly.
#8. Never return an empty answer.
#9. Never return only punctuation or repeated words.
#10. Return only valid JSON.
#
#OUTPUT FORMAT:
#Return exactly one JSON object with exactly these keys:
#{
#  "answer": "...",
#  "ending": "..."
#}
#
#FIELD RULES:
#- answer: direct answer to the customer.
#- ending: one short useful follow-up sentence about the same topic.
#- Do not ask for information that was already answered.
#- Do not ask an unrelated question.
#
#PRICING RULES:
#- If an exact price appears in the content, answer with that price.
#- If several prices appear, list each relevant price clearly.
#- If the exact requested price is missing, say that the exact requested price is not provided.
#- Then mention only the closest relevant prices from the content.
#- Do not invent prices, discounts, taxes, dates, fees, or availability.
#
#COMPLAINT RULES:
#- Content may be empty.
#- Respond with empathy and professionalism.
#- Apologize for the negative experience.
#- Mention the complaint issue if it is clear from the question.
#- Do not promise refund, compensation, replacement, repair, or escalation unless explicitly provided.
#- The ending should ask for one useful next detail, such as reference number, affected product/service, or expected improvement.
#
#VALID JSON RULES:
#- Output valid JSON only.
#- Use double quotes.
#- Do not include markdown.
#- Do not include text before or after the JSON.
#"""

#import os
#import json
#import nltk
#import evaluate
#import numpy as np
#import torch
#
#from datasets import load_dataset
#from transformers import (
#    T5Tokenizer,
#    DataCollatorForSeq2Seq,
#    T5ForConditionalGeneration,
#    Seq2SeqTrainingArguments,
#    Seq2SeqTrainer
#)
#
#MODEL_NAME = "./models/flan-t5-base"
#DATA_FILE = "./data/Dateset_to_flan_t5.jsonl"
#
#OUTPUT_DIR = "./models/trained_flan_t5_base_2"
#RESULTS_DIR = "./results"
#
#tokenizer = T5Tokenizer.from_pretrained(MODEL_NAME)
#model = T5ForConditionalGeneration.from_pretrained(MODEL_NAME)
#
#device = "cuda" if torch.cuda.is_available() else "cpu"
#model.to(device)
#
#model.config.use_cache = False
#model.train()
#
#print("Device:", device)
#
#
#prefix = """
#You are a customer support answer builder.
#
#Input fields:
#topic, question, content.
#
#Task:
#Write a customer support response.
#
#Output format:
#answer: ...
#ending: ...
#
#Rules:
#- Use only the question and content.
#- Do not invent facts, prices, dates, order status, policies, or product details.
#- If exact information is missing, say it is not provided in the available context.
#- For complaint topic, content may be empty.
#- Do not copy instructions into the response.
#- Always include both answer and ending.
#"""
#
#
## Load dataset
#json_answers_qa = load_dataset(
#    "json",
#    data_files=DATA_FILE
#)
#
#json_answers_qa = json_answers_qa["train"].train_test_split(
#    test_size=0.1,
#    seed=42
#)
#
#
#def clean_example(example):
#    topic = str(example.get("topic", "")).strip()
#    question = str(example.get("question", "")).strip()
#    content = str(example.get("content", "")).strip()
#    answer = str(example.get("answer", "")).strip()
#
#    return {
#        "topic": topic,
#        "question": question,
#        "content": content,
#        "answer": answer
#    }
#
#
#json_answers_qa = json_answers_qa.map(clean_example)
#
#json_answers_qa = json_answers_qa.filter(
#    lambda x: (
#        len(x["topic"]) > 0 and
#        len(x["question"]) > 0 and
#        len(x["answer"]) > 0
#    )
#)
#
#
#def normalize_target(answer_text):
#    text = str(answer_text).strip()
#    lower = text.lower()
#
#    if "answer:" in lower and "ending:" in lower:
#        return text
#
#    if "answer:" in lower and "ending:" not in lower:
#        return text + "\nending: Would you like help with the next step?"
#
#    return f"answer: {text}\nending: Would you like help with the next step?"
#
#
#
#def preprocess_function(examples):
#    inputs = []
#
#    for topic, question, content in zip(examples["topic"], examples["question"], examples["content"]):
#        if topic == "complaint":
#            content = ""
#
#        prompt = f"""
#{prefix}
#
#topic:
#{topic}
#
#question:
#{question}
#
#content:
#{content}
#"""
#        inputs.append(prompt)
#
#    targets = [
#      normalize_target(answer)
#      for answer in examples["answer"]
#  ]
#
#    model_inputs = tokenizer(
#        inputs,
#        max_length=768,
#        truncation=True,
#        padding="max_length"
#    )
#
#    labels = tokenizer(
#        text_target=targets,
#        max_length=160,
#        truncation=True,
#        padding="max_length"
#    )
#
#    labels_ids = labels["input_ids"]
#
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
#tokenized_dataset = json_answers_qa.map(
#    preprocess_function,
#    batched=True,
#    remove_columns=json_answers_qa["train"].column_names
#)
#
#
## Label check
#example = tokenized_dataset["train"][0]
#real_labels = sum(1 for x in example["labels"] if x != -100)
#
#decoded_label = tokenizer.decode(
#    [x for x in example["labels"] if x != -100],
#    skip_special_tokens=True
#)
#
#print("Real labels:", real_labels)
#print("Decoded label:")
#print(decoded_label)
#
#if real_labels == 0:
#    raise ValueError("All labels are -100. Stop training.")
#
#
## Manual loss check
#batch = {
#    "input_ids": torch.tensor([example["input_ids"]], dtype=torch.long).to(device),
#    "attention_mask": torch.tensor([example["attention_mask"]], dtype=torch.long).to(device),
#    "labels": torch.tensor([example["labels"]], dtype=torch.long).to(device),
#}
#
#with torch.no_grad():
#    outputs = model(**batch)
#
#manual_loss = outputs.loss.item()
#print("Manual loss:", manual_loss)
#
#if np.isnan(manual_loss):
#    raise ValueError("Manual loss is NaN. Stop training.")
#
#
#data_collator = DataCollatorForSeq2Seq(
#    tokenizer=tokenizer,
#    model=model,
#    label_pad_token_id=-100
#)
#
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
#L_RATE = 5e-6
#BATCH_SIZE = 1
#PER_DEVICE_EVAL_BATCH = 1
#GRADIENT_ACCUMULATION_STEPS = 16
#WEIGHT_DECAY = 0.01
#SAVE_TOTAL_LIM = 2
#NUM_EPOCHS = 3
#
#
#training_args = Seq2SeqTrainingArguments(
#    output_dir=RESULTS_DIR,
#
#    eval_strategy="epoch",
#    save_strategy="epoch",
#
#    learning_rate=L_RATE,
#
#    per_device_train_batch_size=BATCH_SIZE,
#    per_device_eval_batch_size=PER_DEVICE_EVAL_BATCH,
#    gradient_accumulation_steps=GRADIENT_ACCUMULATION_STEPS,
#
#    weight_decay=WEIGHT_DECAY,
#    max_grad_norm=1.0,
#
#    save_total_limit=SAVE_TOTAL_LIM,
#    num_train_epochs=NUM_EPOCHS,
#
#    predict_with_generate=False,
#
#    fp16=False,
#    bf16=False,
#
#    logging_strategy="steps",
#    logging_steps=10,
#
#    report_to="none",
#    dataloader_pin_memory=False,
#    remove_unused_columns=False,
#
#    push_to_hub=False
#)
#
#
#trainer = Seq2SeqTrainer(
#    model=model,
#    args=training_args,
#    train_dataset=tokenized_dataset["train"],
#    eval_dataset=tokenized_dataset["test"],
#    data_collator=data_collator,
#    compute_metrics=None
#)
#
#
#trainer.train()
#
#
#trainer.save_model(OUTPUT_DIR)
#tokenizer.save_pretrained(OUTPUT_DIR)
#
#print("Model saved to:", OUTPUT_DIR)
#
#
## Test generation after training
#model.eval()
#
#test_prompt = f"""
#{prefix}
#
#topic:
#pricing
#
#question:
#How much does it cost to fly from Israel to Greece with El Al in April for one person?
#
#
#content:
#Cheapest flight found | $66
#Roundtrip fares with EL AL Israel Airlines start from $353 next month.
#The cheapest month to fly is January.
#"""
#
#inputs = tokenizer(
#    test_prompt,
#    return_tensors="pt",
#    max_length=768,
#    truncation=True
#).to(device)
#
#with torch.no_grad():
#    generated = model.generate(
#        **inputs,
#        max_new_tokens=160,
#        min_new_tokens=20,
#        do_sample=False,
#        num_beams=4,
#        no_repeat_ngram_size=3,
#        repetition_penalty=1.3,
#        eos_token_id=tokenizer.eos_token_id,
#        pad_token_id=tokenizer.pad_token_id
#    )
#
#print("RAW:", generated[0].tolist())
#print("TEXT WITH SPECIAL:")
#print(tokenizer.decode(generated[0], skip_special_tokens=False))
#print("TEXT:")
#print(tokenizer.decode(generated[0], skip_special_tokens=True))