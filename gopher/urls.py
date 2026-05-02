from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("trending/", views.trending, name="trending"),
    path("hot/", views.hot, name="hot"),
    path("search/", views.search, name="search"),
    path("about/", views.about, name="about"),
    path("post/<path:authorperm>/", views.post_detail, name="post_detail"),
    path("user/<str:username>/", views.profile, name="profile"),
    path("witnesses/", views.witnesses, name="witnesses"),
    path("market/", views.market, name="market"),
    path("feed/", views.feed, name="feed"),
    path("tags/", views.tags, name="tags"),
    path("set-theme/<str:theme_name>/", views.set_theme, name="set_theme"),
    path(
        "login-handshake/<str:username>/", views.login_handshake, name="login_handshake"
    ),
    path("logout/", views.logout, name="logout"),
    path("blocks/", views.block_explorer, name="block_explorer"),
    path("block/<int:block_num>/", views.block_detail, name="block_detail"),
]
