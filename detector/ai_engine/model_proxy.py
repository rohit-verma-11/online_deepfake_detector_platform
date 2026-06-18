import torch
from torchvision import transforms as T
from PIL import Image
from .model import DeepfakeDetector

# Load model once globally to save memory
model = DeepfakeDetector()
model.eval() # Set to evaluation mode

# Image Preprocessing (Standard for ResNet)
transform = T.Compose([
    T.Resize((224, 224)),
    T.ToTensor(),
    T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

def run_inference(frame_paths):
    """
    Takes a list of frame paths and returns (average_score, is_fake)
    """
    if not frame_paths:
        return 0.0, False

    scores = []
    
    with torch.no_grad(): # Disable gradient calculation for speed
        for path in frame_paths:
            image = Image.open(path).convert('RGB')
            image = transform(image).unsqueeze(0) # Add batch dimension
            
            output = model(image)
            scores.append(output.item())

    # Calculate average confidence across all frames
    avg_score = sum(scores) / len(scores)
    
    # Threshold: 0.5 (Adjust based on your model's sensitivity)
    is_fake = avg_score > 0.5
    
    return round(avg_score * 100, 2), is_fake