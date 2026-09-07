import os
import torch

from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForQuestionAnswering
from transformers import AutoModelForSeq2SeqLM
from setfit import SetFitModel
from setfit.model_card import SetFitModelCardData


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")
MODELS_DIR_FLAN = os.path.join(BASE_DIR, "results_flan_t5_customer_support")

DEVICE = "cpu"


def model_path(*parts):
    return os.path.join(MODELS_DIR, *parts)

def model_path_flan(*parts):
    return os.path.join(MODELS_DIR_FLAN, *parts)

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
# 3. SetFit - topic classification
print("Loading SetFit topic model...")

setfit_topic_path = model_path("trained_setfit_topic")

print("SetFit path:", setfit_topic_path)
print("SetFit exists:", os.path.exists(setfit_topic_path))

if not os.path.exists(setfit_topic_path):
    raise FileNotFoundError(f"SetFit model folder not found: {setfit_topic_path}")

print("SetFit files:", os.listdir(setfit_topic_path))

# תיקון לבאג metadata של SetFit במודל מקומי
import setfit.model_card as setfit_model_card

original_infer_st_id = setfit_model_card.SetFitModelCardData.infer_st_id


def safe_infer_st_id(self, model_id):
    try:
        if getattr(self, "st_id", None) is None:
            self.st_id = setfit_topic_path

        if model_id is None:
            return

        return original_infer_st_id(self, model_id)

    except TypeError:
        self.st_id = setfit_topic_path
        return


setfit_model_card.SetFitModelCardData.infer_st_id = safe_infer_st_id

setfit_topic_model = SetFitModel.from_pretrained(
    setfit_topic_path,
    local_files_only=True
)

print("SetFit topic model loaded successfully")



# 4. FLAN-T5 - answer building
print("Loading FLAN-T5 answer model...")
flan_t5_path = model_path_flan("checkpoint-340")

flan_t5_tokenizer = AutoTokenizer.from_pretrained(
    flan_t5_path,
    local_files_only=True,
    use_fast=True
)

flan_t5_model = AutoModelForSeq2SeqLM.from_pretrained(
    flan_t5_path,
    local_files_only=True
)

flan_t5_model.to(DEVICE)
flan_t5_model.eval()

print("FLAN-T5 answer model loaded successfully")


print("========== All models loaded successfully ==========")