from django.contrib import admin
from .models import Category, Course, CourseAuthor, VideoContent, CourseCommentVotes

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

