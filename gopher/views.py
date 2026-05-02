from django.shortcuts import render, redirect
from .services import (
    get_trending_posts,
    get_hot_posts,
    get_post_details,
    get_account_info,
    get_account_blog,
    get_account_feed,
    get_latest_block_num,
    get_block_details,
    get_top_witnesses,
    get_market_ticker,
    get_popular_tags,
    get_random_header,
    get_wallet_data,
)
import urllib.parse


def _get_base_context(request):
    """
    Helper to inject common context like random header and theme.
    """
    # Prefer session-stored theme
    current_theme = request.session.get("theme", "green")
    current_user = request.session.get("hive_user")

    # Safety: Ensure we don't pass the string "None"
    if current_user == "None" or not current_user:
        current_user = None

    return {
        "random_header": get_random_header(),
        "current_theme": current_theme,
        "current_user": current_user,
        "full_path": request.get_full_path(),
    }


def login_handshake(request, username):
    """
    Sets the session user after a successful Keychain signature.
    """
    request.session["hive_user"] = username
    request.session.modified = True
    return redirect("index")


def logout(request):
    """
    Clears the session user.
    """
    if "hive_user" in request.session:
        del request.session["hive_user"]
    return redirect("index")


def set_theme(request, theme_name):
    """
    Sets the theme and redirects back to the previous page, stripping the theme param.
    """
    request.session["theme"] = theme_name
    request.session.modified = True

    next_url = request.GET.get("next", "/")

    # Strip theme param from next_url if it exists to prevent infinite fighting
    url_parts = list(urllib.parse.urlparse(next_url))
    query = dict(urllib.parse.parse_qsl(url_parts[4]))
    query.pop("theme", None)
    url_parts[4] = urllib.parse.urlencode(query)
    clean_next = urllib.parse.urlunparse(url_parts)

    return redirect(clean_next)


def index(request):
    context = _get_base_context(request)
    return render(request, "gopher/index.html", context)


def witnesses(request):
    context = _get_base_context(request)
    context["witnesses"] = get_top_witnesses(limit=20)
    return render(request, "gopher/witnesses.html", context)


def wallet(request, username=None):
    context = _get_base_context(request)

    # If no username provided, use current logged in user
    target_user = username or context.get("current_user")

    if not target_user:
        return redirect("index")

    wallet_data = get_wallet_data(target_user)
    if not wallet_data:
        context["error"] = f"WALLET FOR @{target_user} NOT FOUND."
        return render(request, "gopher/search.html", context)

    context["wallet"] = wallet_data
    return render(request, "gopher/wallet.html", context)


def market(request):
    context = _get_base_context(request)
    context["ticker"] = get_market_ticker()
    return render(request, "gopher/market.html", context)


def feed(request):
    context = _get_base_context(request)
    if not context["current_user"]:
        return redirect("index")

    posts = get_account_feed(context["current_user"])
    context.update({"posts": posts, "title": "My Following Feed"})
    return render(request, "gopher/trending.html", context)


def tags(request):
    context = _get_base_context(request)
    context["tags"] = get_popular_tags(limit=50)
    return render(request, "gopher/tags.html", context)


def trending(request):
    context = _get_base_context(request)
    context.update({"posts": get_trending_posts(limit=15), "title": "Trending"})
    return render(request, "gopher/trending.html", context)


def hot(request):
    context = _get_base_context(request)
    context.update({"posts": get_hot_posts(limit=15), "title": "Hot"})
    return render(request, "gopher/trending.html", context)


def post_detail(request, authorperm):
    context = _get_base_context(request)
    post, replies = get_post_details(authorperm)
    context.update({"post": post, "replies": replies})
    return render(request, "gopher/post_detail.html", context)


def search(request):
    query = request.GET.get("q", "")
    if query:
        if query.startswith("@"):
            return redirect("profile", username=query[1:])
        elif query.startswith("#"):
            context = _get_base_context(request)
            posts = get_trending_posts(limit=15, tag=query[1:])
            context.update({"posts": posts, "title": f"Tag: {query[1:]}"})
            return render(request, "gopher/trending.html", context)
        else:
            return redirect("profile", username=query)

    context = _get_base_context(request)
    return render(request, "gopher/search.html", context)


def profile(request, username):
    account = get_account_info(username)
    if not account:
        context = _get_base_context(request)
        context["error"] = f"ACCOUNT @{username} NOT FOUND."
        return render(request, "gopher/search.html", context)

    context = _get_base_context(request)
    posts = get_account_blog(username)
    context.update({"account": account, "posts": posts})
    return render(request, "gopher/profile.html", context)


def about(request):
    context = _get_base_context(request)
    return render(request, "gopher/about.html", context)


def help(request):
    context = _get_base_context(request)
    return render(request, "gopher/help.html", context)


def block_explorer(request):
    latest = get_latest_block_num()
    blocks = []
    if latest:
        for i in range(latest, latest - 20, -1):
            blocks.append(i)

    context = _get_base_context(request)
    context.update({"blocks": blocks, "latest": latest})
    return render(request, "gopher/block_explorer.html", context)


def block_detail(request, block_num):
    hive_block = get_block_details(block_num)
    context = _get_base_context(request)
    context["hive_block"] = hive_block
    return render(request, "gopher/block_detail.html", context)
