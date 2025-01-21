from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework import status
class TestView(GenericAPIView):
    
    def get(self, request):
        text = "Hello World"
        return Response({'text':text}, status=status.HTTP_200_OK)