from django.db import models

class Category(models.Model):
    name_ka = models.CharField(max_length=255)
    name_en = models.CharField(max_length=255)
    
    def __str__(self):
        return self.name_ka
    
class SubCategory(models.Model):
    name_ka = models.CharField(max_length=255)
    name_en = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.name_ka