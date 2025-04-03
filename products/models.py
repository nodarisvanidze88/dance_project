from django.db import models

class Category(models.Model):
    name_ka = models.CharField(max_length=255, unique=True)
    name_en = models.CharField(max_length=255, unique=True)
    image = models.ImageField(upload_to='category_images/', blank=True, null=True)
    
    def __str__(self):
        return f"{self.name_ka}"
    
class CourseAuthor(models.Model):
    name_ka = models.CharField(max_length=255)
    name_en = models.CharField(max_length=255)
    description_ka = models.TextField(blank=True, null=True)
    description_en = models.TextField(blank=True, null=True)
    school_name_ka = models.CharField(max_length=255, blank=True, null=True)
    school_name_en = models.CharField(max_length=255, blank=True, null=True)
    category = models.ManyToManyField(Category)
    promoted = models.BooleanField(default=False)
    is_new = models.BooleanField(default=False)
    with_discount = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    
    def __str__(self):
        return self.name_ka
    
class SubCategory(models.Model):
    name_ka = models.CharField(max_length=255)
    name_en = models.CharField(max_length=255)
    author = models.ForeignKey(CourseAuthor, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name_ka}"


class VideoContent(models.Model):
    title_ka = models.CharField(max_length=255)
    title_en = models.CharField(max_length=255)
    description_ka = models.TextField(blank=True, null=True)
    description_en = models.TextField(blank=True, null=True)
    video_url = models.URLField()
    sub_category = models.ForeignKey(SubCategory, on_delete=models.CASCADE)
    demo = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    discount_price = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    rank = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"{self.title_ka} - {self.sub_category.name_ka} - {self.sub_category.category.name_ka} - {self.sub_category.category.author.name_ka}"
    
    class Meta:
        ordering = ['rank']
    

    
