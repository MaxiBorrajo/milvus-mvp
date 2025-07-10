import clip
from PIL import Image


model_name = "ViT-B/32"
model, preprocess = clip.load(model_name)
model.eval()


def encode_image(image_path):
    # Si es una lista de rutas, procesar cada una
    if isinstance(image_path, list):
        results = []
        for path in image_path:
            results.append(encode_image(path))
        return results
    
    # Procesar una sola imagen
    image = preprocess(Image.open(image_path)).unsqueeze(0)
    image_features = model.encode_image(image)
    image_features /= image_features.norm(
        dim=-1, keepdim=True
    )  # Normalize the image features
    return image_features.squeeze().tolist()


def encode_text(text):
    # Si es una lista de textos, procesar cada uno
    if isinstance(text, list):
        results = []
        for t in text:
            results.append(encode_text(t))
        return results
    
    # CLIP tiene un límite de contexto de 77 tokens
    # Para evitar errores, truncamos el texto si es demasiado largo
    max_tokens = 70  # Un poco menos que el límite para estar seguros
    
    # Si el texto es muy largo, tomamos solo los primeros caracteres
    # Una aproximación aproximada: 1 token ≈ 4 caracteres
    max_chars = max_tokens * 4
    
    if len(text) > max_chars:
        text = text[:max_chars] + "..."
    
    text_tokens = clip.tokenize(text)
    text_features = model.encode_text(text_tokens)
    text_features /= text_features.norm(
        dim=-1, keepdim=True
    )  # Normalize the text features
    return text_features.squeeze().tolist()
