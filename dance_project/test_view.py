from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework import status
from rest_framework import serializers

class TestViewSerializer(serializers.Serializer):
    text = serializers.CharField()
    class Meta:
        fields = ['text']
        
class TestView(GenericAPIView):
    serializer_class = TestViewSerializer
    def get(self, request):
        text = "Hello World"
        return Response({'text':text}, status=status.HTTP_200_OK)