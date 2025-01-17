from django.contrib import admin
from .models import Category, Language
# Register your models here.

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'language')
    list_filter = ('language',)
    search_fields = ('name',)
admin.site.register(Category,CategoryAdmin)
admin.site.register(Language)