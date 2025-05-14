from django import forms
from .models import Post
from .filters import User


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'author', 'text', 'categories','post_type']
        widgets = {
            'post_type': forms.HiddenInput()  # делаем поле скрытым
        }
    #
    # def save(self, commit=True, post_type=None):
    #     instance = super().save(commit=False)
    #     if post_type:
    #         instance.post_type = post_type
    #     if commit:
    #         instance.save()
    #         self.save_m2m()
    #     return instance


class SearchForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['title'] = forms.CharField(
            required=False,
            widget=forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Поиск по заголовку'
            }),
            label='Заголовок'
        )

        self.fields['author'] = forms.ChoiceField(
            required=False,
            choices=[('', 'Все авторы')] + [
                (user.username, user.username)
                for user in User.objects.all().order_by('username')
            ],
            widget=forms.Select(attrs={'class': 'form-control'}),
            label='Автор'
        )

        self.fields['created_after'] = forms.DateField(
            required=False,
            widget=forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }, format='%Y-%m-%d'),
            label='Дата от'
        )