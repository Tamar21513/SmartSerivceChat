from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import json


model_id="./models/trained_flan_t5_customer_support"

model = AutoModelForSeq2SeqLM.from_pretrained(model_id)
tokenizer = AutoTokenizer.from_pretrained(model_id)






def create_answer(question,context):
    prompt = f"""
You are a customer support assistant.
Answer the question using only the provided context.
Use only information that appears in the text.
Do not ask a new question.
Do not invent, assume, or add missing details.
If the text does not contain enough information, say that clearly.
Return only valid JSON.
Do not add explanations before or after the JSON.

Now answer this:

Question:
{question}

Text:
{context}

JSON:
"""
    inputs = tokenizer(prompt, return_tensors="pt",truncation=True)
    outputs = model.generate(**inputs,max_new_tokens=90,do_sample=False,num_beams=4,early_stopping=True,no_repeat_ngram_size=3,repetition_penalty=1.2)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)


def get_general_topic(question,context):
    prompt = f"""
You are a customer support assistant.
Answer the question using only the provided context.
Use only information that appears in the text.
Do not ask a new question.
Do not invent, assume, or add missing details.
If the text does not contain enough information, say that clearly.
Return only valid JSON.
Do not add explanations before or after the JSON.

Now answer this:

Question:
{question}

Text:
{context}

JSON:
"""
    inputs = tokenizer(prompt, return_tensors="pt",truncation=True)
    outputs = model.generate(**inputs,max_new_tokens=90,do_sample=False,num_beams=4,early_stopping=True,no_repeat_ngram_size=3,repetition_penalty=1.2)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)




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






##----------------------------אימון מודל שכתבתי לבד בסד--------------
#import nltk
#import evaluate
#import numpy as np
#from datasets import load_dataset
#from transformers import T5Tokenizer, DataCollatorForSeq2Seq
#from transformers import T5ForConditionalGeneration, Seq2SeqTrainingArguments, Seq2SeqTrainer
#
#
##MODEL_NAME = "./models/trained_flan_t5_customer_support_3000"
#MODEL_NAME = "./models/trained_flan_t5_customer_support"
#DATA_FILE = "./data/noisy_factual_qa_dataset_150.jsonl"
#
#tokenizer = T5Tokenizer.from_pretrained(MODEL_NAME)
#model = T5ForConditionalGeneration.from_pretrained(MODEL_NAME)
#data_collator = DataCollatorForSeq2Seq(tokenizer=tokenizer, model=model)
#
#json_answers_qa = load_dataset("json",data_files=DATA_FILE)
#
#json_answers_qa = json_answers_qa["train"].train_test_split(test_size=0.3)
#
#json_answers_qa
#
#
#prefix = """
#You are a customer support assistant.
#Answer the question using only the provided context.
#Use only information that appears in the text.
#Do not ask a new question.
#Do not invent, assume, or add missing details.
#If the text does not contain enough information, say that clearly.
#Return only valid JSON.
#Do not add explanations before or after the JSON.
#"""
#
#
#
#
#def preprocess_function(examples):
#    """Add prefix to the sentences, tokenize the text, and set the labels"""
#    inputs = [f"{prefix} Topic: {topic}\nQuestion: {que}\nContext: {con}" for topic , que , con  in zip(examples["topic"] ,examples["question"] , examples["context"])]
#    model_inputs = tokenizer(inputs, max_length=128, truncation=True)
#    terget = [f" answer: {item['answer']}\nending: {item['ending']}" for item in examples["response"]]
#  
#    labels = tokenizer(text_target=terget, 
#                       max_length=512,         
#                       truncation=True) 
#    model_inputs["labels"] = labels["input_ids"]
#    return model_inputs
#
#tokenized_dataset = json_answers_qa.map(preprocess_function, batched=True)
#
#
#
#
##לא צריך - מדדי הצלחה
#nltk.download("punkt", quiet=True)
#metric = evaluate.load("rouge")
#
#
#def compute_metrics(eval_preds):
#   preds, labels = eval_preds
#
#   # decode preds and labels
#   labels = np.where(labels != -100, labels, tokenizer.pad_token_id)
#   decoded_preds = tokenizer.batch_decode(preds, skip_special_tokens=True)
#   decoded_labels = tokenizer.batch_decode(labels, skip_special_tokens=True)
#
#   # rougeLSum expects newline after each sentence
#   decoded_preds = ["\n".join(nltk.sent_tokenize(pred.strip())) for pred in decoded_preds]
#   decoded_labels = ["\n".join(nltk.sent_tokenize(label.strip())) for label in decoded_labels]
#
#   result = metric.compute(predictions=decoded_preds, references=decoded_labels, use_stemmer=True)
#  
#   return result
#
#
## Global Parameters
#L_RATE = 3e-4
#BATCH_SIZE = 8
#PER_DEVICE_EVAL_BATCH = 4
#WEIGHT_DECAY = 0.01
#SAVE_TOTAL_LIM = 3
#NUM_EPOCHS = 3
#
## Set up training arguments
#training_args = Seq2SeqTrainingArguments(
#   output_dir="./results",
#   evaluation_strategy="epoch",
#   learning_rate=L_RATE,
#   per_device_train_batch_size=BATCH_SIZE,
#   per_device_eval_batch_size=PER_DEVICE_EVAL_BATCH,
#   weight_decay=WEIGHT_DECAY,
#   save_total_limit=SAVE_TOTAL_LIM,
#   num_train_epochs=NUM_EPOCHS,
#   predict_with_generate=True,
#   push_to_hub=False
#)
#
#trainer = Seq2SeqTrainer(
#   model=model,
#   args=training_args,
#   train_dataset=tokenized_dataset["train"],
#   eval_dataset=tokenized_dataset["test"],
#   tokenizer=tokenizer,
#   data_collator=data_collator,
#   compute_metrics=compute_metrics
#)
#
#trainer.train()
#
#trainer.save_model("./models/trained_flan_t5_customer_support_3000")
#tokenizer.save_pretrained("./models/trained_flan_t5_customer_support_3000")