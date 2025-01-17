from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import CategoryView

router = DefaultRouter()
router.register('category', CategoryView, basename='category')
urlpatterns = [
    path('category/', CategoryView.as_view(), name='category'),
]