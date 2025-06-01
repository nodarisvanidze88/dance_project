from rest_framework import serializers
from .models import Course, Category, CourseAuthor, VideoContent, CourseCommentVotes

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

class CourseCommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseCommentVotes
        fields = ['course', 'comment', 'vote', 'parent']
        extra_kwargs = {
            'parent': {'required': False, 'allow_null': True},
        }

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)