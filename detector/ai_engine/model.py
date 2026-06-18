import torch
import torch.nn as nn
from torchvision import models

class DeepfakeDetector(nn.Module):
    def __init__(self):
        super(DeepfakeDetector, self).__init__()
        # Using a pre-trained ResNet50 as the feature extractor
        self.network = models.resnet50(pretrained=True)
        
        # Replace the final layer for binary classification (Real vs Fake)
        num_ftrs = self.network.fc.in_features
        self.network.fc = nn.Sequential(
            nn.Linear(num_ftrs, 512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, 1),
            nn.Sigmoid() # Returns a value between 0 and 1
        )

    def forward(self, x):
        return self.network(x)