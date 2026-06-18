from django.db import models
import uuid

class DetectionTask(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    video_file = models.FileField(upload_to="uploads/videos/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    # Analysis Results
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    confidence_score = models.FloatField(null=True, blank=True)  # 0.0 to 1.0
    content_type = models.CharField(max_length=50, blank=True, null=True) # "Animation" or "Real"
    is_fake = models.BooleanField(default=False)
    heatmap_result = models.ImageField(upload_to="results/heatmaps/", null=True, blank=True)
    reasoning = models.TextField()
    def __str__(self):
        return f"Task {self.id} - {self.status}"
    
