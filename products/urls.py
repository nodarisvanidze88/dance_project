from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import CategoryView, BaseCategoryView, AuthorView, SubCategoryView

router = DefaultRouter()
router.register('dance_category', CategoryView, basename='category')
router.register('category', BaseCategoryView, basename='basecategory')
router.register('subcategory', SubCategoryView, basename='subcategory')
router.register('author', AuthorView, basename='author')

urlpatterns = [
    path('dance_category', CategoryView.as_view(), name='category'),
    path('category', BaseCategoryView.as_view(), name='basecategory'),
    path('subcategory', SubCategoryView.as_view(), name='subcategory'),
    path('author', AuthorView.as_view(), name='author'),
]