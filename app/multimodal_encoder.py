from transformers import BlipProcessor, BlipModel
from PIL import Image
import torch

device = "cuda" if torch.cuda.is_available() else "cpu"

processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipModel.from_pretrained("Salesforce/blip-image-captioning-base").to(device)
model.eval()

def encode_text(text: str):
    inputs = processor(text=[text], return_tensors="pt").to(device)
    with torch.no_grad():
        outputs = model.text_model(**inputs)
        embedding = outputs.last_hidden_state.mean(dim=1)  # [batch, hidden_size]
    return embedding.squeeze().cpu().tolist()

def encode_image(image_path: str):
    image = Image.open(image_path).convert("RGB")
    inputs = processor(images=image, return_tensors="pt").to(device)
    with torch.no_grad():
        outputs = model.vision_model(**inputs)
        embedding = outputs.last_hidden_state.mean(dim=1)
    return embedding.squeeze().cpu().tolist()
