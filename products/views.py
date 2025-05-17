from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from .utils import str_to_bool
from drf_yasg.utils import swagger_auto_schema
from django.db.models import Q
from drf_yasg import openapi
from .models import Course, CourseAuthor, VideoContent, CourseCommentVotes
from .serializers import CourseSerializer, VideoContentSerializer

class DanceCategoryAuthorView(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('promoted', openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN),
            openapi.Parameter('is_new', openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN),
            openapi.Parameter('with_discount', openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN),
            openapi.Parameter('search', openapi.IN_QUERY, type=openapi.TYPE_STRING),
            openapi.Parameter('page', openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
        ]
    )
    
    def get(self, request):
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 10))
        offset = (page - 1) * page_size

        filters = Q(is_active=True)
        if (val := request.query_params.get('promoted')) is not None:
            filters &= Q(promoted=str_to_bool(val))
        if (val := request.query_params.get('is_new')) is not None:
            filters &= Q(is_new=str_to_bool(val))
        if (val := request.query_params.get('with_discount')) is not None:
            filters &= Q(with_discount=str_to_bool(val))
        if (val := request.query_params.get('search')) is not None:
            filters &= (
                Q(name_ka__icontains=val) |
                Q(name_en__icontains=val) |
                Q(description_ka__icontains=val) |
                Q(description_en__icontains=val) |
                Q(school_name_ka__icontains=val) |
                Q(school_name_en__icontains=val)
            )

        queryset = CourseAuthor.objects.filter(filters).prefetch_related('category')

        paginated_authors = queryset.order_by('id')[offset:offset + page_size]

        ka_data, en_data = [], []

        for author in paginated_authors:
            for category in author.category.all():
                image_url = request.build_absolute_uri(category.image.url) if category.image else None

                ka_data.append({
                    "category_id": category.id,
                    "category": category.name_ka,
                    "category_image": image_url,
                    "author_data": {
                        "author_id": author.id,
                        "author": author.name_ka,
                        "author_description": author.description_ka,
                        "author_school_name": author.school_name_ka,
                        "author_is_new": author.is_new,
                        "author_promoted": author.promoted,
                        "author_with_discount": author.with_discount,
                    }
                })
                en_data.append({
                    "category_id": category.id,
                    "category": category.name_en,
                    "category_image": image_url,
                    "author_data": {
                        "author_id": author.id,
                        "author": author.name_en,
                        "author_description": author.description_en,
                        "author_school_name": author.school_name_en,
                        "author_is_new": author.is_new,
                        "author_promoted": author.promoted,
                        "author_with_discount": author.with_discount,
                    }
                })

        if not ka_data:
            return Response({"detail": "Not found."}, status=404)
        total_count = len(ka_data)
        return Response({
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_items": total_count,
                "total_pages": (total_count + page_size - 1) // page_size
            },
            "data":{
                "ka": ka_data,
                "en": en_data,
            }  
        }, status=200)

class CourseView(GenericAPIView):
    serializer_class = CourseSerializer
    @swagger_auto_schema(
            manual_parameters=[
                openapi.Parameter(
                    'category_id', 
                    openapi.IN_QUERY, 
                    description="Category ID", 
                    type=openapi.TYPE_INTEGER
                    ),
                openapi.Parameter(
                    'author_id', 
                    openapi.IN_QUERY, 
                    description="Author ID", 
                    type=openapi.TYPE_INTEGER
                    )
                ]
            )
    def get(self, request):
        category_id = request.query_params.get('category_id')
        author_id = request.query_params.get('author_id')
        course_data = Course.objects.all()
        if author_id:
            course_data = course_data.filter(author_id=author_id)
        if category_id:
            course_data = course_data.filter(author__category__id=category_id)
        
        group_data = {'ka':[], 'en':[]}
        for course in course_data:
            data_ka = {
                'course_id': course.id,
                'course': course.name_ka,
                'course_image': request.build_absolute_uri(course.image.url) if course.image else None,
                'course_description': course.description_ka,
                'author_data':{
                    'author_id': course.author.id,
                    'author': course.author.name_ka,
                    'author_description': course.author.description_ka,
                    'author_school_name': course.author.school_name_ka,
                    'author_is_new': course.author.is_new,
                    'author_promoted': course.author.promoted,
                    'author_with_discount': course.author.with_discount
                },
                "rank": course.avg_vote,
                "video_count": course.get_total_videos,
                "total_price": course.get_total_price,
            }
            data_en = {
                'course_id': course.id,
                'course': course.name_en,
                'course_image': request.build_absolute_uri(course.image.url) if course.image else None,
                'course_description': course.description_en,
                'author_data':{
                    'author_id': course.author.id,
                    'author': course.author.name_en,
                    'author_description': course.author.description_en,
                    'author_school_name': course.author.school_name_en,
                    'author_is_new': course.author.is_new,
                    'author_promoted': course.author.promoted,
                    'author_with_discount': course.author.with_discount
                },
                "rank": course.avg_vote,
                "video_count": course.get_total_videos,
                "total_price": course.get_total_price,
            }
            group_data['ka'].append(data_ka)
            group_data['en'].append(data_en)
        return Response(group_data)
    
class VideoContentView(GenericAPIView):
    serializer_class = VideoContentSerializer
    @swagger_auto_schema(
            manual_parameters=[
                openapi.Parameter(
                    'course_id', 
                    openapi.IN_QUERY, 
                    description="course ID", 
                    type=openapi.TYPE_INTEGER
                    )])
    def get(self, request):
        get_course_id = request.query_params.get('course_id')
        video_data = VideoContent.objects.filter(course_id=get_course_id)
        top_level_comments = CourseCommentVotes.objects.filter(course_id=get_course_id, parent__isnull=True)
        def build_comment_tree(comment):
            return {
                'comment_id': comment.id,
                'comment': comment.comment,
                'user': comment.user.username,
                'created_at': comment.created_at,
                'updated_at': comment.updated_at,
                'is_active': comment.is_active,
                'vote': comment.vote,
                'children': [build_comment_tree(child) for child in comment.replies.all()]
            }
        group_data = {'ka':[], 'en':[]}
        for video in video_data:
            data_ka = {
                'video_id': video.id,
                'video_title': video.title_ka,
                'video_description': video.description_ka,
                'video_url': video.video_url,
                'video_demo': video.demo,
                'video_price': video.price,
                'video_discount_price': video.discount_price,
                'video_rank': video.rank,
                'video_is_active': video.is_active,
                'video_created_at': video.created_at,
                'video_updated_at': video.updated_at,
                'course_data':{
                    'course_id': video.course.id,
                    'course': video.course.name_ka,
                },
                'comment_data': [build_comment_tree(comment) for comment in top_level_comments]

            }
            data_en = {
                'video_id': video.id,
                'video_title': video.title_en,
                'video_description': video.description_en,
                'video_url': video.video_url,
                'video_demo': video.demo,
                'video_price': video.price,
                'video_discount_price': video.discount_price,
                'video_rank': video.rank,
                'video_is_active': video.is_active,
                'video_created_at': video.created_at,
                'video_updated_at': video.updated_at,
                'course_data':{
                    'course_id': video.course.id,
                    'course': video.course.name_en,
                },
                'comment_data': [build_comment_tree(comment) for comment in top_level_comments]
            }
            group_data['ka'].append(data_ka)
            group_data['en'].append(data_en)
        return Response(group_data)
    