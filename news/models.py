from random import choices
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum, F
from django.urls import reverse

# Create your models here.
class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)

    def update_rating(self):
        aggregated_data = self.posts.aggregate(
            total_post_rating=Sum(F('rating') * 3),
            total_comments_to_posts_rating=Sum('comments__rating')
            )

        posts_rating = aggregated_data['total_post_rating'] or 0
        comments_to_posts_rating = aggregated_data['total_comments_to_posts_rating'] or 0


        comments_rating = Comment.objects.filter(user=self.user).aggregate(
            total_comment_rating=Sum('rating')
            )['total_comment_rating'] or 0

        self.rating = posts_rating + comments_rating + comments_to_posts_rating
        self.save()

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


ARTICLE = 'AR'
NEWS = 'NW'
POST_TYPES = [
    (ARTICLE, 'Статья'),
    (NEWS, 'Новость'),
]


class Post(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='posts')  # Связь с Author
    post_type = models.CharField(max_length=2, choices=POST_TYPES, default=ARTICLE)  # Выбор: статья или новость
    created_at = models.DateTimeField(auto_now_add=True)  # Дата и время создания (автоматически добавляется)
    categories = models.ManyToManyField('Category', through='PostCategory',related_name='posts')  # Связь "многие ко многим" с Category
    title = models.CharField(max_length=200)
    text = models.TextField()
    rating = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.title}: {self.text}'

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def preview(self):
        return self.text[:124] + ("..." if len(self.text) > 124 else "")

    def get_absolute_url(self):
        return reverse('post_detail', args=[str(self.id)])


class PostCategory(models.Model):
    post = models.ForeignKey('Post', on_delete=models.CASCADE)
    category = models.ForeignKey('Category',on_delete=models.CASCADE)

class Comment(models.Model):
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=0)

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()