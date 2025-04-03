from django.contrib import admin
from .models import Category, SubCategory, CourseAuthor, VideoContent
# Register your models here.    

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name_ka', 'name_en')
    search_fields = ('name_ka', 'name_en')

# class SubCategoryAdmin(admin.ModelAdmin):
#     list_display = ('name_ka', 'category__name_ka','category__author__name_ka','name_en', 'category__name_en','category__author__name_en',)
#     list_filter = ('category__name_ka','category__name_en')
#     search_fields = ('name_ka', 'category__name_ka','category__author__name_ka','name_en', 'category__name_en','category__author__name_en',)
class CourseAuthorAdmin(admin.ModelAdmin):
    list_display = ('name_ka', 'name_en')
    search_fields = ('name_ka','name_en')

# class VideoContentAdmin(admin.ModelAdmin):
#     list_display = ('title_ka', 'sub_category__name_ka','sub_category__category__name_ka','sub_category__category__author__name_ka','title_en', 'sub_category__name_en','sub_category__category__name_en','sub_category__category__author__name_en','rank')
#     search_fields = ('title_ka', 'sub_category__name_ka','sub_category__category__name_ka','sub_category__category__author__name_ka','title_en', 'sub_category__name_en','sub_category__category__name_en','sub_category__category__author__name_en',)
#     list_filter = ('sub_category__name_ka','sub_category__category__name_ka','sub_category__category__author__name_ka','sub_category__name_en','sub_category__category__name_en','sub_category__category__author__name_en',)
#     list_editable = ('rank',)
#     list_display_links = ('title_ka',)
#     list_per_page = 10
#     list_max_show_all = 100

admin.site.register(Category,CategoryAdmin)
admin.site.register(SubCategory)
admin.site.register(CourseAuthor, CourseAuthorAdmin)
admin.site.register(VideoContent)

