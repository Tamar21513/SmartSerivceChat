issueTopic = ["pricing","ordering","tracking","cancel_or_change","returns_and_refunds","account_access","billing_and_payment","technical_issue","product_specs","policy","complaint","date_and_time","other"]
from ModelManager import setfit_topic_model
model = setfit_topic_model

# Predict the issue topic for a question using the SetFit topic model
def categories(question):
    prediction = model.predict([question])
    return issueTopic[prediction[0].item()]


#pricing
#print(categories("How much does it cost?"))
#print(categories("I want to understand the full price of this product, including any extra fees, discounts, or monthly charges before I decide to buy it."))
##ordering
#print(categories("How do I place an order?"))
#print(categories("I found the product I want, but I am not sure what steps I need to follow to complete the order and confirm the purchase."))
##tracking
#print(categories("Where is my order?"))
#print(categories("I placed an order a few days ago and received a confirmation email, but I still do not know where the package is or when it will arrive."))
##cancel_or_change
#print(categories("Can I cancel my order?"))
#print(categories("I made a mistake in my order and I want to know if it is still possible to cancel it or change some of the details before it is shipped."))
##returns_and_refunds
#print(categories("How do I return this item?"))
#print(categories("I received the item, but it does not fit my needs, so I would like to understand how to return it and when I can expect to get a refund."))
##account_access
#print(categories("I can't log in."))
#print(categories("I am trying to access my account, but my password is not working and I am not receiving the reset email, so I need help logging in."))
##billing_and_payment
#print(categories("Why was I charged?"))
#print(categories("I noticed a payment on my account that I do not recognize, and I would like to understand what it is for and whether it can be checked."))
##technical_issue
#print(categories("The website is not working."))
#print(categories("I am trying to use your website, but the page does not load correctly and I keep getting an error message when I try to continue."))
##product_specs
#print(categories("What are the product dimensions?"))
#print(categories("Before I buy this product, I want to know its exact size, weight, materials, and whether it is suitable for daily use."))
##policy
#print(categories("What is your return policy?"))
#print(categories("I would like to understand your company policy regarding returns, refunds, warranty, and how long customers have to report a problem."))
##complaint
#print(categories("I want to file a complaint."))
#print(categories("I am very disappointed with the service I received because my order was delayed, the support team did not answer clearly, and the issue is still unresolved."))
##date_and_time
#print(categories("When will it arrive?"))
#print(categories("I need to know the exact date and time when my order is expected to arrive because I have to make sure someone will be available to receive it."))
##other
#print(categories("What is the capital of Canada?"))
#print(categories("I am preparing a short presentation about renewable energy and would like to understand why solar power has become more popular in many countries over the last decade."))
#print(categories("How much does it cost to fly from Israel to Greece with El Al in April for one person?"))
#print(categories("I have a really good camera and I want to know how to take good pictures."))





#from datasets import load_dataset
#from setfit import TrainingArguments
#from setfit import SetFitModel
#from setfit import Trainer
#
#DATA_FILE = "./data/model1_SetFit_with_other_390.jsonl"
#dataset = load_dataset("json",data_files=DATA_FILE)
#dataset
#
#model = SetFitModel.from_pretrained("./models/all-MiniLM-L6-v2")
#
#json_topic_questions = dataset["train"].train_test_split(test_size=0.3, seed=42)
#json_topic_questions
#
#train_dataset = json_topic_questions["train"]
#test_dataset = json_topic_questions["test"]
#
#args = TrainingArguments(
#    batch_size=32,
#    num_epochs=10,
#)
#
#trainer = Trainer(
#    model=model,
#    args=args,
#    train_dataset=train_dataset,
#)
#
#trainer.train()
#
#model.save_pretrained("./models/trained_setfit_topic")


#from datasets import load_dataset
#from setfit import SetFitModel
#from sklearn.metrics import accuracy_score
#
#DATA_FILE = "./data/model1_SetFit_with_other_390.jsonl"
#
#dataset = load_dataset("json", data_files=DATA_FILE)
#
#json_topic_questions = dataset["train"].train_test_split(test_size=0.3, seed=42)
#
#test_dataset = json_topic_questions["test"]
#
#model = SetFitModel.from_pretrained("./models/trained_setfit_topic")
#
#y_true = test_dataset["label"]
#y_pred = model.predict(test_dataset["text"])
#
#accuracy = accuracy_score(y_true, y_pred)
#
#print(f"Model accuracy: {accuracy * 100:.2f}%")