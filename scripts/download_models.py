#!/usr/bin/env python3
"""
Download required NLP models for bias detection
"""

import subprocess
import sys
import os
from transformers import AutoTokenizer, AutoModelForSequenceClassification

def download_spacy_model():
    """Download spaCy English model"""
    print("Downloading spaCy English model...")
    try:
        subprocess.run([
            sys.executable, "-m", "spacy", "download", "en_core_web_sm"
        ], check=True)
        print("✅ spaCy model downloaded successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to download spaCy model: {e}")
        return False
    except FileNotFoundError:
        print("❌ spaCy not installed. Install with: pip install spacy")
        return False
    return True

def download_transformer_models():
    """Download required transformer models"""
    models = [
        "cardiffnlp/twitter-roberta-base-sentiment-latest",
        "j-hartmann/emotion-english-distilroberta-base"
    ]
    
    for model_name in models:
        print(f"Downloading transformer model: {model_name}")
        try:
            # Download tokenizer and model
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForSequenceClassification.from_pretrained(model_name)
            print(f"✅ {model_name} downloaded successfully")
        except Exception as e:
            print(f"❌ Failed to download {model_name}: {e}")
            return False
    
    return True

def main():
    """Main function to download all models"""
    print("🤖 Downloading NLP models for bias detection...")
    
    success = True
    
    # Download spaCy model
    if not download_spacy_model():
        success = False
    
    # Download transformer models
    if not download_transformer_models():
        success = False
    
    if success:
        print("\n🎉 All models downloaded successfully!")
        print("\nThe bias detection system is now ready to use.")
    else:
        print("\n❌ Some models failed to download.")
        print("Please check your internet connection and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()