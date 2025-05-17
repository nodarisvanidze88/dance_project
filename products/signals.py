from django.db.models.signals import post_delete, pre_save, post_save
from django.db.models import Sum
from django.dispatch import receiver
from .models import Category, VideoContent
import logging
logger = logging.getLogger(__name__)
@receiver(post_delete, sender=Category)
def delete_image_after_category_delete(sender, instance, **kwargs):
    if instance.image:
        instance.image.delete(save=False)

@receiver(pre_save, sender=Category)
def delete_image_on_clear(sender, instance, **kwargs):
    if not instance.pk:
        return  # ახალი ობიექტია, არ ვადარებთ
    
    try:
        old_image = Category.objects.get(pk=instance.pk).image
    except Category.DoesNotExist:
        return

    new_image = instance.image

    if old_image and old_image != new_image:
        old_image.delete(save=False)
        logger.info(f"Deleted image from Space: {instance.image.name}")

@receiver([post_save, post_delete], sender=VideoContent)
def update_course_video_stats(sender, instance, **kwargs):
    course = instance.course
    if course:
        course.total_videos = VideoContent.objects.filter(course=course).count()
        course.total_price = VideoContent.objects.filter(course=course).aggregate(Sum('price'))['price__sum'] or 0.0
        course.save(update_fields=['total_videos', 'total_price'])