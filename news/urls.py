from django.urls import path
from .views import *

app_name = 'news'

urlpatterns = [
    path('', PostsList.as_view(), name='posts_list'),
    path('categories/<int:pk>/', CategoryListView.as_view(), name='category_list'),
    path('category/<int:pk>/', CategoryDetailView.as_view(), name='category_detail'),
    path('subscribe/<int:category_id>/', subscribe, name='subscribe'),
    path('search/', SearchView.as_view(), name='news_search'),
    path('<int:pk>/', PostDetail.as_view(), name='post_detail'),
    path('news/create/', PostCreate.as_view(), name='post_create'),
    path('news/<int:pk>/edit/', PostUpdate.as_view(), name='news_edit'),
    path('news/<int:pk>/delete/', PostDelete.as_view(), name='post_delete'),
    path('articles/create/', PostCreate.as_view(), name='post_create'),
    path('articles/<int:pk>/edit/', PostUpdate.as_view(), name='articles_edit'),
    path('articles/<int:pk>/delete/', PostDelete.as_view(), name='post_delete'),
]