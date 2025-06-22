# The utilities of the Dashboard for the visualization
import re
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from peft import PeftModel, PeftConfig
import sys
import os

# Adding the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import config


def preprocess_transaction(text):
    """Cleaning and normalizing the transaction text"""
    currency_map = {"npr": "₹", "rs": "₹", "rupees": "₹", "$": "USD"} # here using the indian rupee symbol as writing Rs.
    # is little space consuming so using the symbol of indian rupee.
    for term, symbol in currency_map.items():
        text = text.replace(term, symbol)
    return text


def extract_amount(text):
    """Extracting the numerical amount from transaction text"""
    matches = re.findall(r"(\d+\.?\d*)", text)
    return float(matches[0]) if matches else 0.0


def load_model(model_path="../trained_models/finetuned_model"):
    """Loading the trained model for inference"""
    try:
        peft_config = PeftConfig.from_pretrained(model_path)
        base_model = AutoModelForSequenceClassification.from_pretrained(
            peft_config.base_model_name_or_path,
            num_labels=len(config.CATEGORIES),
            id2label=config.id2label,
            label2id=config.label2id
        )
        model = PeftModel.from_pretrained(base_model, model_path)
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        return model, tokenizer
    except Exception as e:
        print(f"⚠️ Error loading fine-tuned model: {str(e)}")
        print("🔄 Loading base model instead")

        model = AutoModelForSequenceClassification.from_pretrained(
            config.MODEL_NAME,
            num_labels=len(config.CATEGORIES),
            id2label=config.id2label,
            label2id=config.label2id
        )
        tokenizer = AutoTokenizer.from_pretrained(config.MODEL_NAME)
        return model, tokenizer
# The utilites for the dashboard visualization here with proper insights of the information