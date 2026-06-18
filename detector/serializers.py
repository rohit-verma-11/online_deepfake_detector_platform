from rest_framework import serializers
from .models import DetectionTask

class DetectionTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetectionTask
        fields = ['id', 'video_file', 'status', 'content_type','confidence_score', 'is_fake', 'uploaded_at','reasoning']
        read_only_fields = ['id', 'status', 'confidence_score', 'is_fake', 'uploaded_at','content_type','reasoning']
