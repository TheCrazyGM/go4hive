from nectar.discussions import Query, Discussions_by_trending, Discussions_by_hot
from nectar.comment import Comment
from nectar.account import Account
import json
import logging

logger = logging.getLogger(__name__)


def get_trending_posts(limit=20, tag=None):
    q = Query(limit=limit, tag=tag)
    return _process_discussions(Discussions_by_trending(q))


def get_hot_posts(limit=20, tag=None):
    q = Query(limit=limit, tag=tag)
    return _process_discussions(Discussions_by_hot(q))


def _process_discussions(discussions):
    posts = []
    for post in discussions:
        # Payout calculation
        total_payout = (
            extract_payout_amount(post.get("pending_payout_value"))
            + extract_payout_amount(post.get("author_payout_value"))
            + extract_payout_amount(post.get("curator_payout_value"))
            + extract_payout_amount(post.get("total_payout_value"))
        )

        # If still 0, check the flat 'payout' field which nectar sometimes provides
        if total_payout == 0:
            total_payout = float(post.get("payout", 0.0))

        # Votes
        stats = post.get("stats", {})
        votes = stats.get("total_votes", post.get("net_votes"))
        if votes is None:
            votes = len(post.get("active_votes", []))

        posts.append(
            {
                "author": post.get("author"),
                "permlink": post.get("permlink"),
                "title": post.get("title"),
                "authorperm": post.get("authorperm"),
                "created": post.get("created"),
                "net_votes": votes,
                "children": post.get("children", 0),
                "payout": total_payout,
            }
        )
    return posts


def get_post_details(authorperm):
    """
    Fetches details for a single post and its comments.
    """
    c = Comment(authorperm)

    total_payout = (
        extract_payout_amount(c.get("pending_payout_value"))
        + extract_payout_amount(c.get("author_payout_value"))
        + extract_payout_amount(c.get("curator_payout_value"))
        + extract_payout_amount(c.get("total_payout_value"))
    )
    if total_payout == 0:
        total_payout = float(c.get("payout", 0.0))

    stats = c.get("stats", {})
    votes = stats.get("total_votes", c.get("net_votes"))
    if votes is None:
        votes = len(c.get("active_votes", []))

    # Process the main post
    post_data = {
        "author": c.get("author"),
        "permlink": c.get("permlink"),
        "title": c.get("title"),
        "body": c.get("body"),
        "created": c.get("created"),
        "net_votes": votes,
        "authorperm": c.get("authorperm"),
        "payout": total_payout,
    }

    # Process replies
    replies = []
    for reply in c.get_replies():
        r_stats = reply.get("stats", {})
        r_votes = r_stats.get("total_votes", reply.get("net_votes"))
        if r_votes is None:
            r_votes = len(reply.get("active_votes", []))

        replies.append(
            {
                "author": reply.get("author"),
                "body": reply.get("body"),
                "created": reply.get("created"),
                "net_votes": r_votes,
                "authorperm": reply.get("authorperm"),
            }
        )

    return post_data, replies


def extract_payout_amount(value):
    """
    Safely extracts a float amount from various Hive payout formats:
    - "26.216 HBD" (string)
    - {'amount': '26.216', 'symbol': 'HBD', ...} (dict)
    - 26.216 (float/int)
    """
    if value is None:
        return 0.0

    # Handle dict format (often seen in newer API responses/nectar objects)
    if isinstance(value, dict):
        return float(value.get("amount", 0.0))

    # Handle string format "1.234 HBD"
    if isinstance(value, str):
        try:
            return float(value.split()[0])
        except ValueError, IndexError:
            return 0.0

    # Handle direct numeric
    if isinstance(value, (int, float)):
        return float(value)

    return 0.0


def get_account_info(username):
    """
    Fetches basic account information.
    """
    try:
        acc = Account(username)

        # Metadata parsing
        metadata = {}
        raw_metadata = acc.get("json_metadata", "")
        if isinstance(raw_metadata, str) and raw_metadata:
            try:
                metadata = json.loads(raw_metadata)
            except json.JSONDecodeError:
                pass
        elif isinstance(raw_metadata, dict):
            metadata = raw_metadata

        profile = metadata.get("profile", {})

        return {
            "name": acc.get("name"),
            "post_count": acc.get("post_count"),
            "reputation": acc.get_reputation(),
            "created": acc.get("created"),
            "about": profile.get("about", "NO DATA"),
        }
    except Exception as e:
        logger.error(f"Error fetching account info for {username}: {e}")
        return None


def get_account_blog(username, limit=10):
    """
    Fetches the blog posts for an account.
    """
    try:
        acc = Account(username)
        posts = []
        for post in acc.get_blog(limit=limit):
            # Vote counting
            votes = post.get("net_votes")
            if votes is None:
                votes = len(post.get("active_votes", []))

            posts.append(
                {
                    "author": post.get("author"),
                    "permlink": post.get("permlink"),
                    "title": post.get("title"),
                    "authorperm": post.get("authorperm"),
                    "created": post.get("created"),
                    "net_votes": votes,
                    "children": post.get("children", 0),
                }
            )
        return posts
    except Exception as e:
        logger.error(f"Error fetching blog for {username}: {e}")
        return []
