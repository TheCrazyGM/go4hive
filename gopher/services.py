from nectar.discussions import (
    Query,
    Discussions_by_trending,
    Discussions_by_hot,
    Trending_tags,
)
from nectar.comment import Comment
from nectar.account import Account
from nectar.blockchain import Blockchain
from nectar.block import Block
from nectar.witness import Witnesses
from nectar.market import Market
from nectar import Hive
import json
import logging
import bleach
import re
import random
from django.core.cache import cache
from .models import HiveCommunity

logger = logging.getLogger(__name__)


def bleach_content(text):
    """
    Strips all HTML tags from the content to keep it text-only.
    """
    if not text:
        return ""
    return bleach.clean(text, tags=[], strip=True)


def resolve_tag_name(tag_name):
    """
    Resolves community identifiers like hive-123456 to human-readable names.
    Uses HiveCommunity model as a persistent cache.
    """
    if not tag_name:
        return ""

    if re.match(r"^hive-\d+$", tag_name):
        # Check local cache first
        cached = HiveCommunity.objects.filter(identifier=tag_name).first()
        if cached:
            return cached.title or cached.name or tag_name

        try:
            hv = Hive()
            payload = {
                "jsonrpc": "2.0",
                "method": "bridge.get_community",
                "params": {"name": tag_name},
                "id": 1,
            }
            res = hv.rpc.rpcexec(payload)

            if res and isinstance(res, dict):
                comm_title = res.get("title")
                comm_name = res.get("name")
                display_name = comm_title or comm_name or tag_name

                HiveCommunity.objects.create(
                    identifier=tag_name, name=comm_name or tag_name, title=comm_title
                )
                return display_name
            else:
                return tag_name
        except Exception as e:
            logger.warning(f"Failed to resolve community {tag_name}: {e}")
            return tag_name

    return tag_name


def get_trending_posts(limit=20, tag=None):
    cache_key = f"trending_{tag}_{limit}"
    data = cache.get(cache_key)
    if data:
        return data

    q = Query(limit=limit, tag=tag)
    data = _process_discussions(Discussions_by_trending(q))
    cache.set(cache_key, data, 60)  # 1 minute
    return data


def get_hot_posts(limit=20, tag=None):
    cache_key = f"hot_{tag}_{limit}"
    data = cache.get(cache_key)
    if data:
        return data

    q = Query(limit=limit, tag=tag)
    data = _process_discussions(Discussions_by_hot(q))
    cache.set(cache_key, data, 60)
    return data


def _process_discussions(discussions):
    posts = []
    for post in discussions:
        total_payout = (
            extract_payout_amount(post.get("pending_payout_value"))
            + extract_payout_amount(post.get("author_payout_value"))
            + extract_payout_amount(post.get("curator_payout_value"))
            + extract_payout_amount(post.get("total_payout_value"))
        )

        if total_payout == 0:
            total_payout = float(post.get("payout", 0.0))

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
    cache_key = f"post_{authorperm}"
    data = cache.get(cache_key)
    if data:
        return data

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

    tags = c.get("tags", [])
    if not tags:
        meta = c.get("json_metadata", {})
        if isinstance(meta, str):
            try:
                meta = json.loads(meta)
            except Exception:
                meta = {}
        tags = meta.get("tags", [])

    resolved_tags = [{"raw": t, "display": resolve_tag_name(t)} for t in tags]

    post_data = {
        "author": c.get("author"),
        "permlink": c.get("permlink"),
        "title": c.get("title"),
        "body": bleach_content(c.get("body")),
        "created": c.get("created"),
        "net_votes": votes,
        "authorperm": c.get("authorperm"),
        "payout": total_payout,
        "tags": resolved_tags,
    }

    replies = []
    for reply in c.get_replies():
        r_stats = reply.get("stats", {})
        r_votes = r_stats.get("total_votes", reply.get("net_votes"))
        if r_votes is None:
            r_votes = len(reply.get("active_votes", []))

        replies.append(
            {
                "author": reply.get("author"),
                "body": bleach_content(reply.get("body")),
                "created": reply.get("created"),
                "net_votes": r_votes,
                "authorperm": reply.get("authorperm"),
            }
        )

    result = (post_data, replies)
    cache.set(cache_key, result, 300)  # 5 minutes
    return result


def extract_payout_amount(value):
    if value is None:
        return 0.0
    if isinstance(value, dict):
        return float(value.get("amount", 0.0))
    if isinstance(value, str):
        try:
            return float(value.split()[0])
        except ValueError, IndexError:
            return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    return 0.0


def get_account_info(username):
    cache_key = f"acc_{username}"
    data = cache.get(cache_key)
    if data:
        return data

    try:
        acc = Account(username)
        metadata = {}
        raw_metadata = acc.get("json_metadata", "")
        if isinstance(raw_metadata, str) and raw_metadata:
            try:
                metadata = json.loads(raw_metadata)
            except Exception:
                pass
        elif isinstance(raw_metadata, dict):
            metadata = raw_metadata

        profile = metadata.get("profile", {})
        data = {
            "name": acc.get("name"),
            "post_count": acc.get("post_count"),
            "reputation": acc.get_reputation(),
            "created": acc.get("created"),
            "about": bleach_content(profile.get("about", "NO DATA")),
        }
        cache.set(cache_key, data, 300)
        return data
    except Exception as e:
        logger.error(f"Error fetching account info for {username}: {e}")
        return None


def get_account_blog(username, limit=10):
    cache_key = f"blog_{username}_{limit}"
    data = cache.get(cache_key)
    if data:
        return data

    try:
        acc = Account(username)
        posts = []
        for post in acc.get_blog(limit=limit):
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
        cache.set(cache_key, posts, 300)
        return posts
    except Exception as e:
        logger.error(f"Error fetching blog for {username}: {e}")
        return []


def get_latest_block_num():
    try:
        chain = Blockchain(mode="irreversible")
        return chain.get_current_block_num()
    except Exception as e:
        logger.error(f"Error getting current block num: {e}")
        return 0


def get_block_details(block_num):
    cache_key = f"block_{block_num}"
    data = cache.get(cache_key)
    if data:
        return data

    block_data = {
        "id": "DATA NOT FOUND",
        "number": block_num,
        "timestamp": "UNKNOWN",
        "witness": "UNKNOWN",
        "transaction_count": 0,
        "raw": "ERROR: BLOCK DATA COULD NOT BE RETRIEVED FROM ANY SOURCE.",
    }

    try:
        block_obj = Block(block_num)
        if not block_obj.get("block_id"):
            chain = Blockchain()
            for b in chain.blocks(start=block_num, stop=block_num):
                block_obj = b
                break

        if not block_obj or not block_obj.get("block_id"):
            hive = Hive()
            rpc_result = hive.rpc.get_block(block_num)
            if rpc_result and "block" in rpc_result:
                block_obj = rpc_result["block"]
            elif rpc_result:
                block_obj = rpc_result

        if block_obj and (block_obj.get("block_id") or block_obj.get("timestamp")):
            raw_serialized = {}
            try:
                raw_serialized = dict(block_obj)
            except Exception:
                if hasattr(block_obj, "items"):
                    raw_serialized = {k: v for k, v in block_obj.items()}
                else:
                    raw_serialized = {
                        "info": "Serialization failed",
                        "type": str(type(block_obj)),
                    }

            block_data.update(
                {
                    "id": block_obj.get("block_id") or block_obj.get("id", "N/A"),
                    "timestamp": block_obj.get("timestamp"),
                    "witness": block_obj.get("witness", "UNKNOWN"),
                    "transaction_count": len(block_obj.get("transactions", [])),
                    "raw": json.dumps(raw_serialized, indent=2, default=str),
                }
            )
            cache.set(cache_key, block_data, 3600)  # 1 hour

    except Exception as e:
        logger.error(f"Critical error in get_block_details for {block_num}: {e}")
        block_data["raw"] = f"SYSTEM ERROR: {str(e)}"

    return block_data


def get_top_witnesses(limit=20):
    cache_key = f"witnesses_{limit}"
    data = cache.get(cache_key)
    if data:
        return data

    try:
        witnesses = []
        all_active = Witnesses()
        for w in all_active:
            raw_votes = w.get("votes", 0)
            try:
                vote_weight = int(raw_votes)
            except Exception:
                vote_weight = 0

            witnesses.append(
                {
                    "owner": w.get("owner"),
                    "votes": vote_weight,
                    "missed": w.get("total_missed", 0),
                    "url": w.get("url"),
                    "signing_key": w.get("signing_key"),
                }
            )

        witnesses.sort(key=lambda x: x["votes"], reverse=True)
        data = witnesses[:limit]
        cache.set(cache_key, data, 300)
        return data
    except Exception as e:
        logger.error(f"Error fetching witnesses: {e}")
        return []


def get_market_ticker():
    cache_key = "market_ticker"
    data = cache.get(cache_key)
    if data:
        return data

    try:
        # Some nodes might be finicky about the pair string, nectar handles it well usually
        m = Market("HIVE:HBD")
        ticker = m.ticker()

        if isinstance(ticker, list) and len(ticker) > 0:
            ticker = ticker[0]

        if not ticker or not isinstance(ticker, dict):
            logger.warning(f"Market ticker returned invalid data type: {type(ticker)}")
            return None

        # Explicitly cast Price and Amount objects to strings to avoid template/serialization issues
        data = {
            "latest": str(ticker.get("latest", "0.000")),
            "lowest_ask": str(ticker.get("lowest_ask", "0.000")),
            "highest_bid": str(ticker.get("highest_bid", "0.000")),
            "percent_change": f"{float(ticker.get('percent_change', 0.0)):.2f}",
            "hive_volume": str(ticker.get("hive_volume", "0.000")),
            "hbd_volume": str(ticker.get("hbd_volume", "0.000")),
        }
        cache.set(cache_key, data, 30)  # 30 seconds
        return data
    except Exception as e:
        logger.error(f"CRITICAL Error fetching market ticker for HIVE:HBD: {e}")
        return None


def get_popular_tags(limit=30):
    cache_key = f"tags_{limit}"
    data = cache.get(cache_key)
    if data:
        return data

    try:
        tags = []
        q = Query(limit=limit)
        for t in Trending_tags(q):
            raw_name = t.get("name")
            tags.append({"raw": raw_name, "display": resolve_tag_name(raw_name)})
        cache.set(cache_key, tags, 600)  # 10 minutes
        return tags
    except Exception as e:
        logger.error(f"Error fetching popular tags: {e}")
        return []


def get_random_header():
    """
    Returns a random curated ASCII art header from figlet.
    """
    headers = [
        # Standard
        """  ____  ___    _  _     _   _ _____     _______
 / ___|/ _ \  | || |   | | | |_ _\ \   / / ____|
| |  _| | | | | || |_  | |_| || | \ \ / /|  _|
| |_| | |_| | |__   _| |  _  || |  \ V / | |___
 \____|\\___/     |_|   |_| |_|___|  \_/  |_____|""",
        # Slant
        """   __________     __ __     __  _______    ________
  / ____/ __ \   / // /    / / / /  _/ |  / / ____/
 / / __/ / / /  / // /_   / /_/ // / | | / / __/
/ /_/ / /_/ /  /__  __/  / __  // /  | |/ / /___
\____/\____/     /_/    /_/ /_/___/  |___/_____/""",
        # Shadow
        """  ___|  _ \   |  |    |   |_ _|\ \     / ____|
 |     |   |  |  |    |   |  |  \ \   /  __|
 |   | |   | ___ __|  ___ |  |   \ \ /   |
\____|\___/     _|   _|  _|___|   \_/   _____| """,
        # Small
        """  ___  ___    _ _    _  _ _____   _____
 / __|/ _ \  | | |  | || |_ _\ \ / / __|
| (_ | (_) | |_  _| | __ || | \ V /| _|
 \___|\\___/    |_|  |_||_|___| \_/ |___|""",
        # Digital
        """+-+-+ +-+ +-+-+-+-+
|G|O| |4| |H|I|V|E|
+-+-+ +-+ +-+-+-+-+""",
    ]
    return random.choice(headers)
