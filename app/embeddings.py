from sentence_transformers import SentenceTransformer
from PIL import Image
import torch

class EmbeddingModel:
    def __init__(self):
        # Load text model
        self.text_model = SentenceTransformer('all-MiniLM-L6-v2')
        # Load clip model for images (using sentence-transformers wrapper for convenience)
        self.clip_model = SentenceTransformer('clip-ViT-B-32')

    def encode_text(self, text: str):
        return self.text_model.encode(text).tolist()

    def encode_image(self, image_path: str):
        img = Image.open(image_path)
        return self.clip_model.encode(img).tolist()

    def encode_text_for_image_search(self, text: str):
        # CLIP-based text embedding to search in image space
        return self.clip_model.encode(text).tolist()
