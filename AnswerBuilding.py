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
    words = question.split()

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

    return tokenizer.decode(outputs[0], skip_special_tokens=True)



#לא נראה לי שצריך--------------------
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
import nltk
import evaluate
import numpy as np
from datasets import load_dataset
from transformers import T5Tokenizer, DataCollatorForSeq2Seq
from transformers import T5ForConditionalGeneration, Seq2SeqTrainingArguments, Seq2SeqTrainer


#MODEL_NAME = "./models/trained_flan_t5_customer_support_3000"
MODEL_NAME = "/google/flan-t5-large"
DATA_FILE = "/content/flan_t5_large_dataset_1200.jsonl"

tokenizer = T5Tokenizer.from_pretrained(MODEL_NAME)
model = T5ForConditionalGeneration.from_pretrained(MODEL_NAME)
data_collator = DataCollatorForSeq2Seq(tokenizer=tokenizer, model=model)

# טעינת קובץ ה-Dataset וחלוקה לנתוני אימון ונתוני בדיקה
json_answers_qa = load_dataset("json", data_files=DATA_FILE)

json_answers_qa = json_answers_qa["train"].train_test_split(
    test_size=0.3,
    seed=42
)


json_answers_qa





# פונקציה שמכינה את הנתונים לאימון:
# מקבלת את הטקסטים מה-Dataset, ממירה אותם לטוקנים,
# ומכינה גם את התשובות הנכונות כ-labels עבור המודל.
def preprocess_function(examples):
    """Add prefix to the sentences, tokenize the text, and set the labels"""
    inputs = examples["input"]    
    model_inputs = tokenizer(inputs, max_length=1024, truncation=True)
    target = examples["output"]
    labels = tokenizer(text_target=target, 
                       max_length=256,         
                       truncation=True) 
    model_inputs["labels"] = labels["input_ids"]
    return model_inputs


# הפעלת פונקציית ההכנה על כל ה-Dataset
# ומחיקת העמודות המקוריות כדי להשאיר רק טוקנים ו-labels
tokenized_dataset = json_answers_qa.map(
    preprocess_function,
    batched=True,
    remove_columns=json_answers_qa["train"].column_names
)



#לא צריך - מדדי הצלחה
nltk.download("punkt", quiet=True)
metric = evaluate.load("rouge")


# פונקציה שמחשבת את איכות המודל בזמן בדיקה:
# משווה בין התשובות שהמודל יצר לבין התשובות הנכונות,
# ומחזירה מדדי ROUGE למדידת דמיון בין הטקסטים.
def compute_metrics(eval_preds):
   preds, labels = eval_preds

   # decode preds and labels
   labels = np.where(labels != -100, labels, tokenizer.pad_token_id)
   decoded_preds = tokenizer.batch_decode(preds, skip_special_tokens=True)
   decoded_labels = tokenizer.batch_decode(labels, skip_special_tokens=True)

   # rougeLSum expects newline after each sentence
   decoded_preds = ["\n".join(nltk.sent_tokenize(pred.strip())) for pred in decoded_preds]
   decoded_labels = ["\n".join(nltk.sent_tokenize(label.strip())) for label in decoded_labels]

   result = metric.compute(predictions=decoded_preds, references=decoded_labels, use_stemmer=True)

   result["quality_percent"] = result["rougeL"] * 100

   return result


# Global Parameters
L_RATE = 3e-5
BATCH_SIZE = 1
PER_DEVICE_EVAL_BATCH = 1
GRADIENT_ACCUMULATION_STEPS = 8
WEIGHT_DECAY = 0.01
SAVE_TOTAL_LIM = 3
NUM_EPOCHS = 5

# הגדרת פרמטרים לאימון המודל
training_args = Seq2SeqTrainingArguments(
    output_dir="./results",
    eval_strategy="epoch",
    save_strategy="epoch",
    learning_rate=L_RATE,
    per_device_train_batch_size=BATCH_SIZE,
    per_device_eval_batch_size=PER_DEVICE_EVAL_BATCH,
    gradient_accumulation_steps=GRADIENT_ACCUMULATION_STEPS,
    weight_decay=WEIGHT_DECAY,
    save_total_limit=SAVE_TOTAL_LIM,
    num_train_epochs=NUM_EPOCHS,
    predict_with_generate=True,
    generation_max_length=256,
    fp16=True,
    push_to_hub=False
)

# יצירת Trainer שמנהל את תהליך האימון, הבדיקה והשמירה
trainer = Seq2SeqTrainer(
   model=model,
   args=training_args,
   train_dataset=tokenized_dataset["train"],
   eval_dataset=tokenized_dataset["test"],
   tokenizer=tokenizer,
   data_collator=data_collator,
   compute_metrics=compute_metrics
)
trainer.train()

# פונקציה שמריצה בדיקה על המודל לאחר האימון:
# מחשבת את איכות המודל לפי ROUGE-L,
# ומחזירה את התוצאה כאחוז.
#אחוז הצלחה
def get_training_percent():
    results = trainer.evaluate()

    percent = results.get("eval_quality_percent", results.get("eval_rougeL", 0) * 100)

    print(f"Training quality percent: {percent:.2f}%")
    return percent

#שימוש באחוז הצלחה
percent = get_training_percent()

trainer.save_model("./models/trained_flan_t5_large")
tokenizer.save_pretrained("./models/trained_flan_t5_large")