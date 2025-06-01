from django.urls import path


from .views import CourseView, VideoContentView, DanceCategoryAuthorView, AddNewCommentView


urlpatterns = [
    path('dance_category/', DanceCategoryAuthorView.as_view(), name='dance_catego_author_view'),
    path('course/', CourseView.as_view(), name='course'),
    # path('author', AuthorView.as_view(), name='author'),
    path('videocontent', VideoContentView.as_view(), name='videocontent'),
    path('add_comment/', AddNewCommentView.as_view(), name='add_comment'),
]