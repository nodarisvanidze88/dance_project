from django.urls import path


from .views import CategoryView, AuthorView, SubCategoryView, VideoContentView, DanceCategoAuthorView


urlpatterns = [
    path('dance_category/', DanceCategoAuthorView.as_view(), name='dance_catego_author_view'),
    path('subcategory', SubCategoryView.as_view(), name='subcategory'),
    path('author', AuthorView.as_view(), name='author'),
    path('videocontent', VideoContentView.as_view(), name='videocontent'),


]