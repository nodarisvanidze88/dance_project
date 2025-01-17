from django.db import models

class Language(models.Model):
    code = models.CharField(max_length=2)

    def __str__(self):
        return self.code
    
class Category(models.Model):
    name = models.CharField(max_length=255)
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.name