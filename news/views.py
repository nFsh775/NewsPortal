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
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404


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

        # if post.post_type == 'NW':
        #     # Получаем всех подписчиков всех категорий поста
        #     domain = Site.objects.get_current().domain
        #     subscribers_sent = set()  # Для избежания дублирования
        #
        #     for category in post.categories.all():
        #         for user in category.subscribers.all():
        #             if user.email and user not in subscribers_sent:
        #                 try:
        #                     subject = f'Новая новость в категории {category.name}: {post.title}'
        #                     html_content = render_to_string(  # Определяем переменную здесь
        #                         'account/email/new_post.html',
        #                         {
        #                             'post': post,
        #                             'user': user,
        #                             'domain': domain,
        #                             'category': category
        #                         }
        #                     )
        #
        #                     send_mail(
        #                         subject=subject,
        #                         message='',  # Текстовый вариант
        #                         from_email='fshhh-11@yandex.ru',
        #                         recipient_list=[user.email],
        #                         html_message=html_content,
        #                         fail_silently=True,
        #                     )
        #                     subscribers_sent.add(user)
        #                 except Exception as e:
        #                     print(f"Ошибка отправки письма: {e}")

        return super().form_valid(form)

    def get_success_url(self):
        # Перенаправляем на страницу созданного поста'fshhh-11@yandex.ru'
        return reverse('news:post_detail', kwargs={'pk': self.object.pk})

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
        return redirect('news:posts_list')

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['is_subscribed'] = self.request.user in self.object.subscribers.all()
        return context


@login_required
def subscribe(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    user = request.user

    if user in category.subscribers.all():
        category.subscribers.remove(user)
        messages.success(request, f'Вы отписались от категории {category.name}')
    else:
        category.subscribers.add(user)
        messages.success(request, f'Вы подписались на категорию {category.name}')

    return redirect('news:category_detail', pk=category_id)
