from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from drf_yasg.utils import swagger_auto_schema
from django.db.models import Q
from drf_yasg import openapi
from .models import SubCategory, Category, CourseAuthor, VideoContent
from .serializers import CategorySerializer, BaseCategorySerializer, AuthorSerializer, SubCategorySerializer, VideoContentSerializer

class AuthorView(GenericAPIView):
    serializer_class = AuthorSerializer
    def get(self, request):
        author_data = CourseAuthor.objects.all()
        group_data = {'ka':[], 'en':[]}
        for author in author_data:
            data_ka = {
                'author_id': author.id,
                'author': author.name_ka,
                'author_description': author.description_ka,
                'author_school_name': author.school_name_ka,
                'author_is_new': author.is_new,
                'author_promoted': author.promoted,
                'author_with_discount': author.with_discount
            }
            data_en = {
                'author_id': author.id,
                'author': author.name_en,
                'author_description': author.description_en,
                'author_school_name': author.school_name_en,
                'author_is_new': author.is_new,
                'author_promoted': author.promoted,
                'author_with_discount': author.with_discount
            }
            group_data['ka'].append(data_ka)
            group_data['en'].append(data_en)
        return Response(group_data)

class BaseCategoryView(GenericAPIView):
    serializer_class = BaseCategorySerializer
    def get(self, request):
        category_data = Category.objects.all()
        group_data = {'ka':[], 'en':[]}
        for category in category_data:
            data_ka = {
                'category_id': category.id,
                'category': category.name_ka,
            }
            data_en = {
                'category_id': category.id,
                'category': category.name_en,
            }
            group_data['ka'].append(data_ka)
            group_data['en'].append(data_en)
        return Response(group_data)

class SubCategoryView(GenericAPIView):
    serializer_class = SubCategorySerializer
    def get(self, request):
        subcategory_data = SubCategory.objects.all()
        group_data = {'ka':[], 'en':[]}
        for subcategory in subcategory_data:
            data_ka = {
                'category_id': subcategory.id,
                'category': subcategory.name_ka,
            }
            data_en = {
                'category_id': subcategory.id,
                'category': subcategory.name_en,
            }
            group_data['ka'].append(data_ka)
            group_data['en'].append(data_en)
        return Response(group_data)

class CategoryView(GenericAPIView):
    serializer_class = CategorySerializer
    @swagger_auto_schema(
            manual_parameters=[
                openapi.Parameter(
                    'author_id', 
                    openapi.IN_QUERY, 
                    description="Author ID", 
                    type=openapi.TYPE_INTEGER
                    ),
                openapi.Parameter(
                    'category_id', 
                    openapi.IN_QUERY, 
                    description="Category ID", 
                    type=openapi.TYPE_INTEGER
                    ),
                openapi.Parameter(
                    'subcategory_id', 
                    openapi.IN_QUERY, 
                    description="SubCategory ID", 
                    type=openapi.TYPE_INTEGER
                    ),
                openapi.Parameter(
                    'search', 
                    openapi.IN_QUERY, 
                    description="Search term", 
                    type=openapi.TYPE_STRING
                    ),
                openapi.Parameter(
                    'promoted', 
                    openapi.IN_QUERY, 
                    description="Promoted", 
                    type=openapi.TYPE_BOOLEAN
                    ),
                openapi.Parameter(
                    'is_new', 
                    openapi.IN_QUERY, 
                    description="Is New", 
                    type=openapi.TYPE_BOOLEAN
                    ),
                openapi.Parameter(
                    'with_discount', 
                    openapi.IN_QUERY, 
                    description="With Discount", 
                    type=openapi.TYPE_BOOLEAN
                    ),
                     
                ]
            )
    def get(self, request):
        category_id = request.query_params.get('category_id')
        subcategory_id = request.query_params.get('subcategory_id')
        author_id = request.query_params.get('author_id')
        search = request.query_params.get('search')
        promoted = request.query_params.get('promoted')
        is_new = request.query_params.get('is_new')
        with_discount = request.query_params.get('with_discount')
        filters = {}
        if category_id:
            filters['category_id'] = category_id
        if subcategory_id:
            filters['id'] = subcategory_id
        if author_id:
            filters['category__author_id'] = author_id
        if promoted == 'true':
            filters['category__author__promoted'] = True
        if is_new == 'true':
            filters['category__author__is_new'] = True
        if with_discount == 'true':
            filters['category__author__with_discount'] = True

        
        subCategories = SubCategory.objects.filter(**filters).order_by('-category__author__promoted', 
                                                                       '-category__author__is_new',
                                                                       '-category__author__with_discount')
        if search:
            search_filters = (
                Q(name_ka__icontains=search) |
                Q(name_en__icontains=search) |
                Q(category__name_ka__icontains=search) |
                Q(category__name_en__icontains=search) |
                Q(category__author__name_ka__icontains=search) |
                Q(category__author__name_en__icontains=search) |
                Q(category__author__description_ka__icontains=search) |
                Q(category__author__description_en__icontains=search) |
                Q(category__author__school_name_ka__icontains=search) |
                Q(category__author__school_name_en__icontains=search)
            )
            subCategories = SubCategory.objects.filter(search_filters).order_by('-category__author__promoted', 
                                                                                '-category__author__is_new',
                                                                                '-category__author__with_discount')
        group_data = {'ka':[], 'en':[]}
        for subcategory in subCategories:
            data_ka = {
                'author_id': subcategory.category.author.id,
                'author': subcategory.category.author.name_ka,
                'author_description': subcategory.category.author.description_ka,
                'author_school_name': subcategory.category.author.school_name_ka,
                'author_is_new': subcategory.category.author.is_new,
                'author_promoted': subcategory.category.author.promoted,
                'author_with_discount': subcategory.category.author.with_discount,
                'category_data':{
                    'category_id': subcategory.category.id,
                    'category': subcategory.category.name_ka,
                    'subcategory_data':{
                        'subcategory_id': subcategory.id,
                        'subcategory': subcategory.name_ka
                    }
                }
                
            }
            data_en = {
                'author_id': subcategory.category.author.id,
                'author': subcategory.category.author.name_en,
                'author_description': subcategory.category.author.description_en,
                'author_school_name': subcategory.category.author.school_name_en,
                'author_is_new': subcategory.category.author.is_new,
                'author_promoted': subcategory.category.author.promoted,
                'author_with_discount': subcategory.category.author.with_discount,
                'category_data':{
                    'category_id': subcategory.category.id,
                    'category': subcategory.category.name_en,
                    'subcategory_data':{
                        'subcategory_id': subcategory.id,
                        'subcategory': subcategory.name_en
                    }
                }
                
            }
            group_data['ka'].append(data_ka)
            group_data['en'].append(data_en)
        if not group_data['ka']:
            return Response({"detail": "Not found."}, status=404)
        return Response(group_data)
    
class VideoContentView(GenericAPIView):
    serializer_class = VideoContentSerializer
    @swagger_auto_schema(
            manual_parameters=[
                openapi.Parameter(
                    'subcategory_id', 
                    openapi.IN_QUERY, 
                    description="Subcategory ID", 
                    type=openapi.TYPE_INTEGER
                    )])
    def get(self, request):
        get_subcategory_id = request.query_params.get('subcategory_id')
        video_data = VideoContent.objects.filter(sub_category_id=get_subcategory_id)
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
                'subcategory_data':{
                    'subcategory_id': video.sub_category.id,
                    'subcategory': video.sub_category.name_ka,
                    'category_data':{
                        'category_id': video.sub_category.category.id,
                        'category': video.sub_category.category.name_ka,
                        'author_data':{
                            'author_id': video.sub_category.category.author.id,
                            'author': video.sub_category.category.author.name_ka,
                            'author_description': video.sub_category.category.author.description_ka,
                            'author_school_name': video.sub_category.category.author.school_name_ka,
                            'author_is_new': video.sub_category.category.author.is_new,
                            'author_promoted': video.sub_category.category.author.promoted,
                            'author_with_discount': video.sub_category.category.author.with_discount
                        }
                    }
                }
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
                'subcategory_data':{
                    'subcategory_id': video.sub_category.id,
                    'subcategory': video.sub_category.name_en,
                    'category_data':{
                        'category_id': video.sub_category.category.id,
                        'category': video.sub_category.category.name_en,
                        'author_data':{
                            'author_id': video.sub_category.category.author.id,
                            'author': video.sub_category.category.author.name_en,   
                            'author_description': video.sub_category.category.author.description_en,
                            'author_school_name': video.sub_category.category.author.school_name_en,
                            'author_is_new': video.sub_category.category.author.is_new,
                            'author_promoted': video.sub_category.category.author.promoted,
                            'author_with_discount': video.sub_category.category.author.with_discount
                        }
                    }
                }
            }
            group_data['ka'].append(data_ka)
            group_data['en'].append(data_en)
        return Response(group_data)
    