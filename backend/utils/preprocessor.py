import re

class TextPreprocessor:
    def clean(self, text):
        # Remove URLs
        text = re.sub(r'http\S+|www\S+', '', text)
        # Remove special characters
        text = re.sub(r'[^a-zA-Z0-9\s\.\,\!\?\-\&]', '', text)
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text
