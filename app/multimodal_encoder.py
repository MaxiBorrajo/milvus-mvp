from transformers import CLIPModel, CLIPProcessor
from PIL import Image
import torch

class CLIPMultimodal:
    def __init__(self, model_name: str, model_processor: str):
        self.model = CLIPModel.from_pretrained(model_name)
        self.model.eval()
        self.model_processor = CLIPProcessor.from_pretrained(model_processor)

    def encode_textos(self, textos: list[str]) -> list[list[float]]:
        datos = self.model_processor(text=textos, return_tensors="pt", padding=True, truncation=True)
        with torch.no_grad():
            vectores = self.model.get_text_features(**datos)
        return vectores.tolist()
    
    def encode_imagenes(self, imagenes: list[str]) -> list[list[float]]:
        imagenes = [Image.open(imagen).convert("RGB") for imagen in imagenes]
        datos = self.model_processor(images=imagenes, return_tensors="pt")
        with torch.no_grad():
            vectores = self.model.get_image_features(**datos)
        return vectores.tolist()
    
    # El processor siempre recibe una lista de textos/imagenes entonces no tiene sentido hacer un metodo unitario para procesar una sola imagen o texto, se lo puede pasar como una lista de un elemento.

