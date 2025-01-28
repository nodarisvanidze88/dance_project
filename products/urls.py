from django.urls import path


from .views import CategoryView, BaseCategoryView, AuthorView, SubCategoryView, VideoContentView


urlpatterns = [
    path('dance_category', CategoryView.as_view(), name='category'),
    path('category', BaseCategoryView.as_view(), name='basecategory'),
    path('subcategory', SubCategoryView.as_view(), name='subcategory'),
    path('author', AuthorView.as_view(), name='author'),
    path('videocontent', VideoContentView.as_view(), name='videocontent'),


]