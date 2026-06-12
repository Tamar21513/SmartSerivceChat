import os
import torch

from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForQuestionAnswering
from transformers import AutoModelForSeq2SeqLM
from setfit import SetFitModel


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")

DEVICE = "cpu"


def model_path(*parts):
    return os.path.join(MODELS_DIR, *parts)


print("========== Loading all models once ==========")


# 1. Sentence Transformer - embeddings
print("Loading SentenceTransformer...")
embedding_model = SentenceTransformer(
    model_path("all-MiniLM-L6-v2")
)


# 2. DistilBERT - Question Answering
print("Loading DistilBERT QA...")
distilbert_path = model_path("distilbert-base-cased-distilled-squad")

distilbert_tokenizer = AutoTokenizer.from_pretrained(
    distilbert_path,
    local_files_only=True
)

distilbert_model = AutoModelForQuestionAnswering.from_pretrained(
    distilbert_path,
    local_files_only=True
)

distilbert_model.to(DEVICE)
distilbert_model.eval()


# 3. SetFit - topic classification
print("Loading SetFit topic model...")
setfit_topic_model = SetFitModel.from_pretrained(
    model_path("trained_setfit_topic")
)


# 4. FLAN-T5 - answer building
print("Loading FLAN-T5 answer model...")
flan_t5_path = model_path("trained_flan_t5_large")

flan_t5_tokenizer = AutoTokenizer.from_pretrained(
    flan_t5_path,
    local_files_only=True
)

flan_t5_model = AutoModelForSeq2SeqLM.from_pretrained(
    flan_t5_path,
    local_files_only=True
)

flan_t5_model.to(DEVICE)
flan_t5_model.eval()


print("========== All models loaded successfully ==========")