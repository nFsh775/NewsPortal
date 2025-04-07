from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from .models import Post
from .filters import PostFilter
from .forms import PostForm,SearchForm
from django.core.paginator import Paginator
from django.urls import reverse
from django.shortcuts import redirect


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

class PostCreate(CreateView):
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'


    def form_valid(self, form):
        post = form.save(commit=False)
        # Определяем тип поста на основе URL
        if 'news/create' in self.request.path:
            post.post_type = 'NW'
        elif 'articles/create' in self.request.path:
            post.post_type = 'AR'
        post.save()  # Сохраняем пост после установки типа
        return super().form_valid(form)

    def get_success_url(self):
        # Перенаправляем на страницу созданного поста
        return reverse('post_detail', kwargs={'pk': self.object.pk})

class PostUpdate(UpdateView):
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'
    success_url = reverse_lazy('posts_list')

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
