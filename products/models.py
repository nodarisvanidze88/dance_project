from django.db import models


class CourseAuthor(models.Model):
    name_ka = models.CharField(max_length=255)
    name_en = models.CharField(max_length=255)
    description_ka = models.TextField(blank=True, null=True)
    description_en = models.TextField(blank=True, null=True)
    school_name_ka = models.CharField(max_length=255, blank=True, null=True)
    school_name_en = models.CharField(max_length=255, blank=True, null=True)
    promoted = models.BooleanField(default=False)
    is_new = models.BooleanField(default=False)
    with_discount = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name_ka
    
class Category(models.Model):
    name_ka = models.CharField(max_length=255)
    name_en = models.CharField(max_length=255)
    author = models.ForeignKey(CourseAuthor, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.name_ka} - {self.author.name_ka}"
    
class SubCategory(models.Model):
    name_ka = models.CharField(max_length=255)
    name_en = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.name_ka
    
