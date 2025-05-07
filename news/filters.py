from django_filters import FilterSet, ChoiceFilter, DateFilter, CharFilter
from django import forms
from .models import Post
from django.contrib.auth import get_user_model

User = get_user_model()

class PostFilter(FilterSet):
    title = CharFilter(
        lookup_expr='icontains',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Поиск по заголовку'}),
        label='Заголовок'
    )

    author = ChoiceFilter(
        field_name='author__user__username',
        choices=[],  # Список будет заполнен динамически
        lookup_expr='exact',
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Автор'
    )

    created_after = DateFilter(
        field_name='created_at',
        lookup_expr='gte',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}, format='%Y-%m-%d'),
        label='Дата от'
    )

    class Meta:
        model = Post
        fields = ['title', 'author', 'created_after']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters['author'].extra['choices'] = [
            (user.username, user.username)
            for user in User.objects.all().order_by('username')
        ]


