# detector/ai_engine/content_classifier.py
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image

# MobileNet is very light and perfect for "Real vs Animation"
content_model = models.mobilenet_v2(pretrained=True)
# Change the final layer to 2 classes: [Animation, Real]
content_model.classifier[1] = nn.Linear(content_model.last_channel, 2)
content_model.eval()

def is_real_video(frame_path):
    """
    Returns True if the content is Real Life, False if Animation/CGI.
    """
    image = Image.open(frame_path).convert('RGB')
    preprocess = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    
    input_tensor = preprocess(image).unsqueeze(0)
    
    with torch.no_grad():
        output = content_model(input_tensor)
        # Class 0: Animation, Class 1: Real
        probabilities = torch.nn.functional.softmax(output[0], dim=0)
        return probabilities[1] > 0.5