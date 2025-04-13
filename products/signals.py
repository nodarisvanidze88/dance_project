from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from .models import Category

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
