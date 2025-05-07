from django.db import migrations


def fix_data(apps, schema_editor):
    Post = apps.get_model('news', 'Post')
    PostCategory = apps.get_model('news', 'PostCategory')

    # 1. Удалить битые связи
    PostCategory.objects.exclude(post__in=Post.objects.all()).delete()

    # 2. Перенумеровать оставшиеся записи
    for index, item in enumerate(PostCategory.objects.all(), start=1):
        item.id = index
        item.save()


class Migration(migrations.Migration):
    dependencies = [
        ('news', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(fix_data),
    ]
