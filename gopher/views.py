from django.shortcuts import render, redirect
from .services import (
    get_trending_posts,
    get_hot_posts,
    get_post_details,
    get_account_info,
    get_account_blog,
    get_latest_block_num,
    get_block_details,
    get_top_witnesses,
    get_market_ticker,
    get_popular_tags,
)


def index(request):
    return render(request, "gopher/index.html")


def witnesses(request):
    witness_list = get_top_witnesses(limit=20)
    return render(request, "gopher/witnesses.html", {"witnesses": witness_list})


def market(request):
    ticker = get_market_ticker()
    return render(request, "gopher/market.html", {"ticker": ticker})


def tags(request):
    popular_tags = get_popular_tags(limit=50)
    return render(request, "gopher/tags.html", {"tags": popular_tags})


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


def block_explorer(request):
    latest = get_latest_block_num()
    blocks = []
    if latest:
        # Show latest 20 blocks
        for i in range(latest, latest - 20, -1):
            blocks.append(i)
    return render(
        request, "gopher/block_explorer.html", {"blocks": blocks, "latest": latest}
    )


def block_detail(request, block_num):
    hive_block = get_block_details(block_num)
    return render(request, "gopher/block_detail.html", {"hive_block": hive_block})
