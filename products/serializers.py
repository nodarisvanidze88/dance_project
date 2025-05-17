from rest_framework import serializers
from .models import Course, Category, CourseAuthor, VideoContent

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseAuthor
        fields = '__all__'
        
class BaseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'
        
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class VideoContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoContent
        fields = '__all__'