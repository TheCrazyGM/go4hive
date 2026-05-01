from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('trending/', views.trending, name='trending'),
    path('hot/', views.hot, name='hot'),
    path('search/', views.search, name='search'),
    path('about/', views.about, name='about'),
    path('post/<path:authorperm>/', views.post_detail, name='post_detail'),
    path('user/<str:username>/', views.profile, name='profile'),
]
