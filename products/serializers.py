from rest_framework import serializers
from .models import Course, Category, CourseAuthor, VideoContent, CourseCommentVotes, CourseVote

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

class CourseVoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseVote
        fields = ['course', 'vote']
        
    def validate_vote(self, value):
        if value not in [1, 2, 3, 4, 5]:
            raise serializers.ValidationError("Vote must be between 1 and 5")
        return value
    
    def validate_course(self, value):
        if not Course.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Course does not exist")
        return value
    
    def create(self, validated_data):
        user = self.context['request'].user
        course = validated_data['course']
        vote = validated_data['vote']
        
        # Update or create vote
        course_vote, created = CourseVote.objects.update_or_create(
            user=user,
            course=course,
            defaults={'vote': vote}
        )
        return course_vote