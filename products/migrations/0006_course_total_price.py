# Generated by Django 5.1.5 on 2025-05-17 21:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0005_remove_videocontent_sub_category_course_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='total_price',
            field=models.FloatField(default=0),
        ),
    ]
