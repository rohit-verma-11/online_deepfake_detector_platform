from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import DetectionTask
from .serializers import DetectionTaskSerializer
from .tasks import process_video_detection

class DetectionViewSet(viewsets.ModelViewSet):
    queryset = DetectionTask.objects.all()
    serializer_class = DetectionTaskSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Save the video to the database
            task = serializer.save()
            print(f"Manually triggering task for {task.id}")
            process_video_detection.delay(task.id)
            # --- NEXT STEP PREVIEW ---
            # This is where we will trigger Celery:
            # detect_deepfake_task.delay(task.id)
            
            return Response({
                "message": "Upload successful. Analysis started.",
                "task_id": task.id
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        task = serializer.save()
        # This triggers the background worker!
        print(f"DEBUG: Triggering task for ID {task.id}")
        process_video_detection.delay(task.id)
