from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import CategoryView, SubCategoryView

router = DefaultRouter()
router.register('category', CategoryView, basename='category')
router.register('subcategory', SubCategoryView, basename='subcategory')
urlpatterns = [
    path('category', CategoryView.as_view(), name='category'),
    path('subcategory', SubCategoryView.as_view(), name='subcategory'),
]