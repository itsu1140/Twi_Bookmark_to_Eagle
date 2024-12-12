import os
import sys
import errno
import aiohttp
from datetime import datetime, timezone

from twikit import Client


def get_website(username: str, id: str):
    return f"https://x.com/{username}/status/{id}/"


def have_media(tweet):
    return hasattr(tweet, "media") and tweet.media


def have_quote(tweet):
    return hasattr(tweet, "quote") and tweet.quote is not None


async def bookmark2eagle(cookie_path: str, twi_num: int = 30):
    client = Client(language="ja")
    try:
        if os.path.exists(cookie_path):
            client.load_cookies(cookie_path)
        else:
            raise FileNotFoundError(
                errno.ENOENT, os.strerror(errno.ENOENT), cookie_path
            )

        bookmarks = await client.get_bookmarks(count=twi_num)

        items = []
        for bookmark in bookmarks:
            item = {
                "tags": [],
                "modificationTime": int(datetime.now(timezone.utc).timestamp() * 1000),
                "headers": {"referer": "x.com"},
            }
            if not have_media(bookmark):
                if bookmark.thumbnail_url:
                    item["url"] = bookmark.thumbnail_url
                    item["name"] = f"@{bookmark.user.screen_name} {bookmark.text}"
                    item["website"] = get_website(
                        bookmark.user.screen_name, bookmark.id
                    )
                    items.append(item)
                if have_quote(bookmark) and have_media(bookmark.quote):
                    item["url"] = bookmark.quote.media[0].get("media_url_https")
                    item["name"] = (
                        f"@{bookmark.quote.user.screen_name} {bookmark.quote.text}"
                    )
                    item["website"] = get_website(
                        bookmark.quote.user.screen_name, bookmark.quote.id
                    )
                    items.append(item)
                continue
            for media in bookmark.media:
                item["url"] = media.get("media_url_https")
                item["name"] = f"@{bookmark.user.screen_name} {bookmark.text}"
                item["website"] = get_website(bookmark.user.screen_name, bookmark.id)
                items.append(item)

        data = {"items": items}

        # Send the POST request
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "http://127.0.0.1:41595/api/item/addFromURLs", json=data
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    print(result)
                    for bookmark in bookmarks:
                        if not have_media(bookmark):
                            if (
                                bookmark.thumbnail_url
                                or have_quote(bookmark)
                                and have_media(bookmark.quote)
                            ):
                                await bookmark.delete_bookmark()
                            continue
                        await bookmark.delete_bookmark()
                else:
                    print(f"Failed to post data: {response.status}")

    except Exception as error:
        _, _, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_no = exception_traceback.tb_lineno
        raise Exception(
            f"{filename}の{line_no}行目でエラーが発生しました。詳細：{error}"
        )
