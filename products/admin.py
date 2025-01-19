from django.contrib import admin
from .models import Category, SubCategory
# Register your models here.

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name_ka', 'name_en')
    search_fields = ('name_ka','name_en')

class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ('name_ka', 'name_en', 'category__name_ka','category__name_en')
    list_filter = ('category__name_ka','category__name_en')
    search_fields = ('name_ka','name_en','category__name_ka','category__name_en')

admin.site.register(Category,CategoryAdmin)
admin.site.register(SubCategory,SubCategoryAdmin)
