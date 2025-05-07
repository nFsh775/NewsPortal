from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from .models import Post
from .models import Category
from .filters import PostFilter
from .forms import PostForm,SearchForm
from django.core.paginator import Paginator
from django.urls import reverse
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import get_object_or_404, render
from django import forms
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.mail import send_mail
from django.template.loader import render_to_string

class PostsList(ListView):
    model = Post
    ordering = '-created_at'
    template_name = 'news.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = PostFilter(self.request.GET, queryset)
        return self.filterset.qs


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        return context


class PostDetail(DetailView):
    model = Post
    template_name = 'new.html'
    context_object_name = 'post'

class PostCreate(PermissionRequiredMixin,CreateView):
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'

    def get_permission_required(self):
        post_type = self.kwargs.get('post_type')
        if post_type == 'news':
            return ['news.add_post']  # Право на создание новостей
        return ['news.add_post']  # Право на создание статей

    def form_valid(self, form):
        post = form.save(commit=False)
        # Определяем тип поста на основе URL
        if 'news/create' in self.request.path:
            post.post_type = 'NW'
        elif 'articles/create' in self.request.path:
            post.post_type = 'AR'
        post.save()  # Сохраняем пост после установки типа
        form.save_m2m()

        if post.post_type == 'NW':  # Отправляем только для новостей
            subscribers = post.categories.subscribers.all()
            if subscribers:
                subject = f'Новая новость в категории {post.categories.name}: {post.title}'

                for user in subscribers:
                    html_content = render_to_string(
                        'email/new_post.html',
                        {
                            'user': user,
                            'post': post,
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

        return super().form_valid(form)

    def get_success_url(self):
        # Перенаправляем на страницу созданного поста
        return reverse('post_detail', kwargs={'pk': self.object.pk})

class PostUpdate(LoginRequiredMixin,PermissionRequiredMixin,UpdateView):
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'
    success_url = reverse_lazy('posts_list')
    login_url = reverse_lazy('login')

    def get_permission_required(self):
        post = self.get_object()
        if post.post_type == 'news':
            return ['news.change_post']
        return ['news.change_post']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post_type'] = self.kwargs.get('post_type')
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = PostFilter(self.request.GET, queryset)
        return self.filterset.qs

    def form_valid(self, form):
        post = form.save()
        return redirect('posts_list')

class PostDelete(DeleteView):
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('posts_list')

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = PostFilter(self.request.GET, queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post_type'] = self.kwargs.get('post_type')
        return context

class SearchView(TemplateView):
    template_name = 'search.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = SearchForm(self.request.GET or None)
        context['form'] = form
        queryset = Post.objects.all().order_by('-created_at')

        if form.is_valid():
            data = form.cleaned_data

            if data.get('title'):
                queryset = queryset.filter(title__icontains=data['title'])

            if data.get('author'):
                queryset = queryset.filter(author__user__username=data['author'])

            if data.get('created_after'):
                queryset = queryset.filter(created_at__gte=data['created_after'])

        paginator = Paginator(queryset, self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context['posts'] = page_obj.object_list
        context['page_obj'] = page_obj
        context['paginator'] = paginator

        return context

class ProtectedView(LoginRequiredMixin, TemplateView):
    template_name = 'news.html'

    def post_list(request):
        posts = Post.objects.all()
        return render(request, 'news/category_list.html', {'posts': posts})

class PostForm(forms.ModelForm):
    Category = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label='Категории'
    )

    class Meta:
        model = Post
        fields = ['title', 'text', 'Category']


class CategoryListView(ListView):
    model = Post
    template_name = 'news/category_list.html'
    context_object_name = 'category_news_list'

    def get_queryset(self):
        self.category = get_object_or_404(Category, pk=self.kwargs['pk'])
        queryset = Post.objects.filter(categories=self.category).order_by('-created_at')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_subscriber'] = self.request.user not in self.category.subscribers.all()
        context['category'] = self.category
        return context

class CategoryDetailView(DetailView):
    model = Category
    template_name = 'news/category_detail.html'
    context_object_name = 'category'

@login_required
def subscribe(request, category_id):
    category = Category.objects.get(id=category_id)
    if request.user in category.subscribers.all():
        category.subscribers.remove(request.user)
    else:
        category.subscribers.add(request.user)
    return redirect('news:category_detail', pk=category_id)
