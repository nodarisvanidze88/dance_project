from django.urls import path


from .views import CourseView, VideoContentView, DanceCategoryAuthorView, CommentView, CourseVoteView, MediaAssetListView


urlpatterns = [
    path('dance_category/', DanceCategoryAuthorView.as_view(), name='dance_catego_author_view'),
    path('course/', CourseView.as_view(), name='course'),
    path('videocontent/', VideoContentView.as_view(), name='videocontent'),
    path('comment/', CommentView.as_view(), name='comment'),
    path('vote/', CourseVoteView.as_view(), name='course_vote'),  # New endpoint
    path('media-assets/', MediaAssetListView.as_view(), name='media_assets'),
]