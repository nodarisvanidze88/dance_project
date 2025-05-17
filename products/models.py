from django.db import models
from storages.backends.s3boto3 import S3Boto3Storage
from accounts.models import CustomUser
from django.db.models import Sum

class Category(models.Model):
    name_ka = models.CharField(max_length=255, unique=True)
    name_en = models.CharField(max_length=255, unique=True)
    image = models.ImageField(upload_to='category_images/', blank=True, null=True, storage=S3Boto3Storage())
    
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
    
class CourseCommentVotes(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    comment = models.TextField()
    course = models.ForeignKey("Course", on_delete=models.CASCADE, related_name='comments', blank=True, null=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='replies')
    child = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='children')
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    vote = models.IntegerField(default=0,choices=[(0, 0),(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], blank=True, null=True)
    def __str__(self):
        return f"{self.user} - {self.course.name_ka}"

class Course(models.Model):
    name_ka = models.CharField(max_length=255)
    name_en = models.CharField(max_length=255)
    description_ka = models.TextField(blank=True, null=True)
    description_en = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='course_images/', blank=True, null=True, storage=S3Boto3Storage())
    author = models.ForeignKey(CourseAuthor, on_delete=models.CASCADE)
    rank = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    total_videos = models.IntegerField(default=0)
    total_price = models.FloatField(default=0)

    @property
    def avg_vote(self):
        sum_votes = self.comments.aggregate(Sum('vote'))['vote__sum']
        count_votes = self.comments.count()
        if count_votes > 0:
            self.rank = sum_votes / count_votes
        else:
            self.rank = 0
        return self.rank
    
    @property
    def get_total_videos(self):
        # self.total_videos = VideoContent.objects.filter(course=self).count()
        return self.total_videos
    
    @property
    def get_total_price(self):
        # result = VideoContent.objects.filter(course=self).aggregate(Sum('price'))
        # self.total_price = result['price__sum'] or 0.0
        return self.total_price
        
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        # Only after it's saved (and has a pk), calculate the dependent fields
        self.rank = self.avg_vote
        self.total_videos = self.get_total_videos
        self.total_price = self.get_total_price

        if not is_new:  # avoid infinite recursion
            super().save(update_fields=['rank', 'total_videos', 'total_price'])


    def __str__(self):
        return f"{self.name_ka}"




class VideoContent(models.Model):
    title_ka = models.CharField(max_length=255)
    title_en = models.CharField(max_length=255)
    description_ka = models.TextField(blank=True, null=True)
    description_en = models.TextField(blank=True, null=True)
    video_url = models.URLField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='videos', blank=True, null=True)
    demo = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    discount_price = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    rank = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        course_name = self.course.name_ka if self.course else "No Course"
        author_name = self.course.author.name_ka if self.course and self.course.author else "No Author"
        return f"{self.title_ka} - {course_name} - {author_name}"


    class Meta:
        ordering = ['rank']
    

    
