from django.contrib import admin
from .models import Category, SubCategory, CourseAuthor
# Register your models here.    

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name_ka', "author__name_ka",'name_en',"author__name_en")
    search_fields = ('name_ka',"author__name_ka",'name_en',"author__name_en")

class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ('name_ka', 'category__name_ka','category__author__name_ka','name_en', 'category__name_en','category__author__name_en',)
    list_filter = ('category__name_ka','category__name_en')
    search_fields = ('name_ka', 'category__name_ka','category__author__name_ka','name_en', 'category__name_en','category__author__name_en',)
class CourseAuthorAdmin(admin.ModelAdmin):
    list_display = ('name_ka', 'name_en')
    search_fields = ('name_ka','name_en')

admin.site.register(Category,CategoryAdmin)
admin.site.register(SubCategory,SubCategoryAdmin)
admin.site.register(CourseAuthor, CourseAuthorAdmin)

