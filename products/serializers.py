from rest_framework import serializers
from .models import SubCategory, Category, CourseAuthor, VideoContent

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseAuthor
        fields = '__all__'
class BaseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = '__all__'
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = '__all__'

class VideoContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoContent
        fields = '__all__'