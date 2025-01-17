from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from .serializers import CategorySerializer
from .models import Category

class CategoryView(GenericAPIView):
    def get(self, request):
        categories = Category.objects.all()

        group_data = {}
        for category in categories:
            lang_code = category.language.code
            if lang_code not in group_data:
                group_data[lang_code] = {'language': lang_code, 'data': []}
            group_data[lang_code]['data'].append({
                'id': category.id,
                'name': category.name
            })
        return Response(list(group_data.values()))
