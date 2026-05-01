from django.shortcuts import render, redirect
from .services import (
    get_trending_posts,
    get_hot_posts,
    get_post_details,
    get_account_info,
    get_account_blog,
)


def index(request):
    return render(request, "gopher/index.html")


def trending(request):
    posts = get_trending_posts(limit=15)
    return render(
        request, "gopher/trending.html", {"posts": posts, "title": "Trending"}
    )


def hot(request):
    posts = get_hot_posts(limit=15)
    return render(request, "gopher/trending.html", {"posts": posts, "title": "Hot"})


def post_detail(request, authorperm):
    post, replies = get_post_details(authorperm)
    return render(
        request, "gopher/post_detail.html", {"post": post, "replies": replies}
    )


def search(request):
    query = request.GET.get("q", "")
    if query:
        if query.startswith("@"):
            return redirect("profile", username=query[1:])
        elif query.startswith("#"):
            posts = get_trending_posts(limit=15, tag=query[1:])
            return render(
                request,
                "gopher/trending.html",
                {"posts": posts, "title": f"Tag: {query[1:]}"},
            )
        else:
            return redirect("profile", username=query)
    return render(request, "gopher/search.html")


def profile(request, username):
    account = get_account_info(username)
    if not account:
        return render(
            request, "gopher/search.html", {"error": f"ACCOUNT @{username} NOT FOUND."}
        )

    posts = get_account_blog(username)
    return render(request, "gopher/profile.html", {"account": account, "posts": posts})


def about(request):
    return render(request, "gopher/about.html")
