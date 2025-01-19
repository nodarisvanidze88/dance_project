from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Category, SubCategory
from .serializers import SubcategorySerializer, CategorySerializer
class CategoryView(GenericAPIView):
    serializer_class = CategorySerializer
    def get(self, request):
        categories = Category.objects.all()
        group_data = {'ka':[], 'en':[]}
        for category in categories:
            group_data['ka'].append({
                'id': category.id,
                'category': category.name_ka
            })
            group_data['en'].append({
                'id': category.id,
                'category': category.name_en
            })
        return Response(group_data)

class SubCategoryView(GenericAPIView):
    serializer_class = SubcategorySerializer
    @swagger_auto_schema(
            manual_parameters=[
                openapi.Parameter(
                    'category_id', 
                    openapi.IN_QUERY, 
                    description="Category ID", 
                    type=openapi.TYPE_INTEGER
                    )
                ]
            )
    def get(self, request):
        category_id = request.query_params.get('category_id')
        if category_id:
            subCategories = SubCategory.objects.filter(category_id=category_id)
        else:
            subCategories = SubCategory.objects.all()
        group_data = {'ka':[], 'en':[]}
        for subcategory in subCategories:
            group_data['ka'].append({
                'id': subcategory.id,
                'category': subcategory.category.name_ka,
                'subcategory': subcategory.name_ka
            })
            group_data['en'].append({
                'id': subcategory.id,
                'category': subcategory.category.name_en,
                'subcategory': subcategory.name_en
            })
        return Response(group_data)