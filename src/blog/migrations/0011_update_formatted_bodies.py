from django.db import migrations, models

def populate_formatted_bodies(apps, schema_editor):
    Post = apps.get_model('blog', 'Post')
    for obj in Post.objects.all():
        obj.formatted_body = obj.excerpt
        obj.save()
        

class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0010_rename_body_post_excerpt_post_formatted_body_and_more'),
    ]

    operations = [
        migrations.RunPython(populate_formatted_bodies, reverse_code=migrations.RunPython.noop),
    ]
