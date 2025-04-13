from django.contrib import admin
from .models import Category, SubCategory, CourseAuthor, VideoContent

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name_ka', 'name_en')
    search_fields = ('name_ka', 'name_en')
    
class CourseAuthorAdmin(admin.ModelAdmin):
    list_display = ('name_ka', 'name_en')
    search_fields = ('name_ka','name_en')

admin.site.register(Category,CategoryAdmin)
admin.site.register(SubCategory)
admin.site.register(CourseAuthor, CourseAuthorAdmin)
admin.site.register(VideoContent)

