from django.contrib import admin
from .models import Category, Course, CourseAuthor, VideoContent, CourseCommentVotes, MediaAsset

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name_ka', 'name_en')
    search_fields = ('name_ka', 'name_en')
    
class CourseAuthorAdmin(admin.ModelAdmin):
    list_display = ('name_ka', 'name_en')
    search_fields = ('name_ka','name_en')
admin.site.register(CourseCommentVotes)
admin.site.register(Category,CategoryAdmin)
admin.site.register(Course)
admin.site.register(CourseAuthor, CourseAuthorAdmin)
admin.site.register(VideoContent)
@admin.register(MediaAsset)
class MediaAssetAdmin(admin.ModelAdmin):
    list_display = ("name", "asset_type", "is_active", "created_at")
    list_filter = ("asset_type", "is_active")
    search_fields = ("name",)

