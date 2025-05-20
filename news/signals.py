from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.sites.models import Site
from .models import Post
from django.utils import timezone
from datetime import timedelta


@receiver(post_save, sender=Post)
def handle_post_save(sender, instance, created, **kwargs):
    if created and instance.post_type == 'NW':
        send_notifications_to_subscribers(instance)

def send_notifications_to_subscribers(post):
    domain = Site.objects.get_current().domain
    subscribers_sent = set()

    for category in post.categories.all():
        for user in category.subscribers.all():
            if user.email and user not in subscribers_sent:
                try:
                    subject = f'Новая новость в категории {category.name}: {post.title}'
                    html_content = render_to_string(
                        'email/new_post.html',
                        {
                            'post': post,
                            'user': user,
                            'domain': domain,
                            'category': category
                        }
                    )

                    send_mail(
                        subject=subject,
                        message='',
                        from_email='fshhh-11@yandex.ru',
                        recipient_list=[user.email],
                        html_message=html_content,
                        fail_silently=True,
                    )
                    subscribers_sent.add(user)
                except Exception as e:
                    print(f"Ошибка отправки письма: {e}")


@receiver(post_save, sender=Post)
def check_news_limit(sender, instance, **kwargs):
    if instance.pk is None and instance.post_type == 'NW':
        twenty_four_hours_ago = timezone.now() - timedelta(hours=24)
        news_count = Post.objects.filter(
            author=instance.author,
            post_type='NW',
            created_at__gte=twenty_four_hours_ago
        ).count()

        if news_count >= 3:
            from django.core.exceptions import ValidationError
            raise ValidationError('Вы превысили лимит публикаций (3 новости в сутки)')
