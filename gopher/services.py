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
from nectar.community import Community
from nectar import Hive
import json
import logging
import bleach
import re
from .models import HiveCommunity

logger = logging.getLogger(__name__)


def bleach_content(text):
    """
    Strips all HTML tags from the content to keep it text-only.
    """
    if not text:
        return ""
    # Bleach with no allowed tags to strip everything
    return bleach.clean(text, tags=[], strip=True)


def resolve_tag_name(tag_name):
    """
    Resolves community identifiers like hive-123456 to human-readable names.
    Uses HiveCommunity model as a persistent cache.
    """
    if not tag_name:
        return ""

    # Check for hive-XXXXXX pattern
    if re.match(r"^hive-\d+$", tag_name):
        # Check local cache first
        cached = HiveCommunity.objects.filter(identifier=tag_name).first()
        if cached:
            return cached.title or cached.name or tag_name

        # Not in cache, fetch from blockchain
        try:
            # We use a simple Hive instance; NodeList might be overkill here but good for production
            hv = Hive()
            comm = Community(tag_name, blockchain_instance=hv)
            # Some communities have 'title', some use 'name' as the display label
            comm_title = comm.get("title")
            comm_name = comm.get("name")

            display_name = comm_title or comm_name or tag_name

            # Save to cache
            HiveCommunity.objects.create(
                identifier=tag_name, name=comm_name or tag_name, title=comm_title
            )
            return display_name
        except Exception as e:
            logger.warning(f"Failed to resolve community {tag_name}: {e}")
            return tag_name

    return tag_name


def get_trending_posts(limit=20, tag=None):
    q = Query(limit=limit, tag=tag)
    return _process_discussions(Discussions_by_trending(q))


def get_hot_posts(limit=20, tag=None):
    q = Query(limit=limit, tag=tag)
    return _process_discussions(Discussions_by_hot(q))


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

    # Handle tags - they can be in 'tags' or 'json_metadata'
    tags = c.get("tags", [])
    if not tags:
        metadata = c.get("json_metadata", {})
        if isinstance(metadata, str):
            try:
                metadata = json.loads(metadata)
            except Exception:
                metadata = {}
        tags = metadata.get("tags", [])

    # Resolve tag names for display
    resolved_tags = []
    for t in tags:
        resolved_tags.append({"raw": t, "display": resolve_tag_name(t)})

    # Process the main post
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
                "body": bleach_content(reply.get("body")),
                "created": reply.get("created"),
                "net_votes": r_votes,
                "authorperm": reply.get("authorperm"),
            }
        )

    return post_data, replies


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
            "about": bleach_content(profile.get("about", "NO DATA")),
        }
    except Exception as e:
        logger.error(f"Error fetching account info for {username}: {e}")
        return None


def get_account_blog(username, limit=10):
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


def get_latest_block_num():
    try:
        chain = Blockchain(mode="irreversible")
        return chain.get_current_block_num()
    except Exception as e:
        logger.error(f"Error getting current block num: {e}")
        return 0


def get_block_details(block_num):
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

    except Exception as e:
        logger.error(f"Critical error in get_block_details for {block_num}: {e}")
        block_data["raw"] = f"SYSTEM ERROR: {str(e)}"

    return block_data


def get_top_witnesses(limit=20):
    """
    Fetches the active witnesses and sorts them by votes.
    Using the Witnesses() class ensures we get the current active set.
    """
    try:
        witnesses = []
        # Witnesses() class correctly identifies the active set
        all_active = Witnesses()
        for w in all_active:
            # Handle vote weight (often represented as a huge integer/string)
            raw_votes = w.get("votes", 0)
            try:
                vote_weight = int(raw_votes)
            except ValueError, TypeError:
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

        # Sort descending by votes
        witnesses.sort(key=lambda x: x["votes"], reverse=True)
        return witnesses[:limit]
    except Exception as e:
        logger.error(f"Error fetching witnesses: {e}")
        return []


def get_market_ticker():
    """
    Fetches the latest ticker info for HIVE:HBD.
    """
    try:
        m = Market("HIVE:HBD")
        ticker = m.ticker()
        return {
            "latest": ticker.get("latest"),
            "lowest_ask": ticker.get("lowest_ask"),
            "highest_bid": ticker.get("highest_bid"),
            "percent_change": ticker.get("percent_change"),
            "hive_volume": ticker.get("hive_volume"),
            "hbd_volume": ticker.get("hbd_volume"),
        }
    except Exception as e:
        logger.error(f"Error fetching market ticker: {e}")
        return None


def get_popular_tags(limit=30):
    """
    Fetches popular/trending tags and resolves community names.
    """
    try:
        tags = []
        q = Query(limit=limit)
        for t in Trending_tags(q):
            raw_name = t.get("name")
            tags.append({"raw": raw_name, "display": resolve_tag_name(raw_name)})
        return tags
    except Exception as e:
        logger.error(f"Error fetching popular tags: {e}")
        return []
