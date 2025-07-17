from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .utils import str_to_bool
from drf_yasg.utils import swagger_auto_schema
from django.db.models import Q
from drf_yasg import openapi
from .models import Course, CourseAuthor, VideoContent, CourseCommentVotes
from .serializers import CourseSerializer, VideoContentSerializer, CourseCommentCreateSerializer
from rest_framework.permissions import IsAuthenticated
from payments.models import PaymentOrder

# class DanceCategoryAuthorView(APIView):
#     permission_classes = [IsAuthenticated]
#     @swagger_auto_schema(
#         manual_parameters=[
#             openapi.Parameter('promoted', openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN),
#             openapi.Parameter('is_new', openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN),
#             openapi.Parameter('with_discount', openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN),
#             openapi.Parameter('search', openapi.IN_QUERY, type=openapi.TYPE_STRING),
#             openapi.Parameter('page', openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
#             openapi.Parameter('page_size', openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
#         ]
#     )
    
#     def get(self, request):
#         page = int(request.query_params.get('page', 1))
#         page_size = int(request.query_params.get('page_size', 10))
#         offset = (page - 1) * page_size

#         filters = Q(is_active=True)
#         if (val := request.query_params.get('promoted')) is not None:
#             filters &= Q(promoted=str_to_bool(val))
#         if (val := request.query_params.get('is_new')) is not None:
#             filters &= Q(is_new=str_to_bool(val))
#         if (val := request.query_params.get('with_discount')) is not None:
#             filters &= Q(with_discount=str_to_bool(val))
#         if (val := request.query_params.get('search')) is not None:
#             filters &= (
#                 Q(name_ka__icontains=val) |
#                 Q(name_en__icontains=val) |
#                 Q(description_ka__icontains=val) |
#                 Q(description_en__icontains=val) |
#                 Q(school_name_ka__icontains=val) |
#                 Q(school_name_en__icontains=val)
#             )

#         queryset = CourseAuthor.objects.filter(filters).prefetch_related('category')

#         paginated_authors = queryset.order_by('id')[offset:offset + page_size]

#         ka_data, en_data = [], []

#         for author in paginated_authors:
#             for category in author.category.all():
#                 image_url = request.build_absolute_uri(category.image.url) if category.image else None

#                 ka_data.append({
#                     "category_id": category.id,
#                     "category": category.name_ka,
#                     "category_image": image_url,
#                     "author_data": {
#                         "author_id": author.id,
#                         "author": author.name_ka,
#                         "author_description": author.description_ka,
#                         "author_school_name": author.school_name_ka,
#                         "author_is_new": author.is_new,
#                         "author_promoted": author.promoted,
#                         "author_with_discount": author.with_discount,
#                     }
#                 })
#                 en_data.append({
#                     "category_id": category.id,
#                     "category": category.name_en,
#                     "category_image": image_url,
#                     "author_data": {
#                         "author_id": author.id,
#                         "author": author.name_en,
#                         "author_description": author.description_en,
#                         "author_school_name": author.school_name_en,
#                         "author_is_new": author.is_new,
#                         "author_promoted": author.promoted,
#                         "author_with_discount": author.with_discount,
#                     }
#                 })

#         if not ka_data:
#             return Response([], status=200)
#         total_count = len(ka_data)
#         return Response({
#             "pagination": {
#                 "page": page,
#                 "page_size": page_size,
#                 "total_items": total_count,
#                 "total_pages": (total_count + page_size - 1) // page_size
#             },
#             "data":{
#                 "ka": ka_data,
#                 "en": en_data,
#             }  
#         }, status=200)
class DanceCategoryAuthorView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('promoted', openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN),
            openapi.Parameter('is_new', openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN),
            openapi.Parameter('with_discount', openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN),
            openapi.Parameter('search', openapi.IN_QUERY, type=openapi.TYPE_STRING),
        ]
    )
    def get(self, request):
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

        queryset = CourseAuthor.objects.filter(filters).prefetch_related('category', 'course_set')

        group_data = {'ka': [], 'en': []}

        for author in queryset:
            courses = author.course_set.all()

            # Calculate totals
            total_videos = sum(course.get_total_videos for course in courses)
            total_price = sum(course.get_total_price for course in courses)
            rank_values = [course.avg_vote for course in courses if course.avg_vote is not None]
            avg_rank = round(sum(rank_values) / len(rank_values), 2) if rank_values else None

            for category in author.category.all():
                image_url = request.build_absolute_uri(category.image.url) if category.image else None

                data_ka = {
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
                    },
                    "rank": avg_rank,
                    "video_count": total_videos,
                    "total_price": total_price,
                }

                data_en = {
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
                    },
                    "rank": avg_rank,
                    "video_count": total_videos,
                    "total_price": total_price,
                }

                group_data['ka'].append(data_ka)
                group_data['en'].append(data_en)

        return Response(group_data, status=200)

class CourseView(GenericAPIView):
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]
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
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'course_id',
                openapi.IN_QUERY,
                description="course ID",
                type=openapi.TYPE_INTEGER
            )
        ])
    def get(self, request):
        user = request.user
        course_id = request.query_params.get('course_id')
        video_data = VideoContent.objects.filter(course_id=course_id)

        # Get set of video IDs the user has paid for
        paid_video_ids = set(
            PaymentOrder.objects.filter(user=user, status="paid")
            .values_list("videos__id", flat=True)
        )
        print("this is paid video ids", paid_video_ids)

        group_data = {'ka': [], 'en': []}
        for video in video_data:
            has_access = video.id in paid_video_ids

            data_ka = {
                'video_id': video.id,
                'video_title': video.title_ka,
                'video_description': video.description_ka,
                'video_url': video.video_url if has_access or video.demo else None,
                'video_thumbnail': request.build_absolute_uri(video.thumbnail.url) if video.thumbnail else None,
                'video_demo': video.demo,
                'video_price': video.price,
                'video_discount_price': video.discount_price,
                'video_rank': video.rank,
                'video_is_active': video.is_active,
                'video_created_at': video.created_at,
                'video_updated_at': video.updated_at,
                'course_data': {
                    'course_id': video.course.id if video.course else None,
                    'course': video.course.name_ka if video.course else None,
                },
            }
            data_en = {
                'video_id': video.id,
                'video_title': video.title_en,
                'video_description': video.description_en,
                'video_url': video.video_url if has_access or video.demo else None,
                'video_thumbnail': request.build_absolute_uri(video.thumbnail.url) if video.thumbnail else None,
                'video_demo': video.demo,
                'video_price': video.price,
                'video_discount_price': video.discount_price,
                'video_rank': video.rank,
                'video_is_active': video.is_active,
                'video_created_at': video.created_at,
                'video_updated_at': video.updated_at,
                'course_data': {
                    'course_id': video.course.id if video.course else None,
                    'course': video.course.name_en if video.course else None,
                },
            }

            group_data['ka'].append(data_ka)
            group_data['en'].append(data_en)

        return Response(group_data)

class CommentView(GenericAPIView):
    serializer_class = CourseCommentCreateSerializer
    permission_classes = [IsAuthenticated]
    def build_comment_tree(self, comment):
        return {
            'comment_id': comment.id,
            'comment': comment.comment,
            'user': comment.user.username,
            'created_at': comment.created_at,
            'updated_at': comment.updated_at,
            'is_active': comment.is_active,
            'vote': comment.vote,
            'children': [self.build_comment_tree(child) for child in comment.replies.all()]
        }

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'course_id',
                openapi.IN_QUERY,
                description="Course ID",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={200: "List of comments with nested replies"}
    )
    def get(self, request):
        course_id = request.query_params.get('course_id')
        if not course_id:
            return Response({"detail": "course_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        top_level_comments = CourseCommentVotes.objects.filter(course_id=course_id, parent__isnull=True)
        comments_tree = [self.build_comment_tree(comment) for comment in top_level_comments]
        return Response(comments_tree)
    @swagger_auto_schema(
        request_body=CourseCommentCreateSerializer,
        responses={201: "Comment added successfully", 400: "Bad Request"}
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            comment = serializer.save()
            return Response({
                "message": "Comment added successfully",
                "comment_id": comment.id
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
