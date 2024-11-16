import os
import sys
import errno
import aiohttp
import asyncio

from twikit import Client
from dotenv import load_dotenv
from datetime import datetime, timezone

twi_num = 30


async def main(cookie_path):

    client = Client(language="ja")
    load_dotenv()
    try:
        if os.path.exists(cookie_path):
            client.load_cookies(cookie_path)
        else:
            raise FileNotFoundError(
                errno.ENOENT, os.strerror(errno.ENOENT), cookie_path)

        bookmarks = await client.get_bookmarks(count=twi_num)

        items = []
        for bookmark in bookmarks:
            if not hasattr(bookmark, 'media') or not bookmark.media:
                if bookmark.thumbnail_url:
                    items.append({
                        "url": bookmark.thumbnail_url,
                        "name": f"@{bookmark.user.screen_name} {bookmark.text}",
                        "website": f"https://x.com/{bookmark.user.screen_name}/status/{bookmark.id}/",
                        "tags": [],
                        "modificationTime": int(datetime.now(timezone.utc).timestamp()*1000),
                        "headers": {
                            "referer": "x.com"
                        }
                    })
                if hasattr(bookmark, 'quote') and bookmark.quote is not None:
                    if hasattr(bookmark.quote, 'media') and bookmark.quote.media is not None:
                        items.append({
                            "url": bookmark.quote.media[0].get('media_url_https'),
                            "name": f"@{bookmark.quote.user.screen_name} {bookmark.quote.text}",
                            "website": f"https://x.com/{bookmark.quote.user.screen_name}/status/{bookmark.quote.id}/",
                            "tags": [],
                            "modificationTime": int(datetime.now(timezone.utc).timestamp()*1000),
                            "headers": {
                                "referer": "x.com"
                            }
                        })
                    continue
                continue
            for i, media in enumerate(bookmark.media):
                items.append({
                    "url": media.get('media_url_https'),
                    "name": f"@{bookmark.user.screen_name} {bookmark.text}",
                    "website": f"https://x.com/{bookmark.user.screen_name}/status/{bookmark.id}/",
                    "tags": [],
                    "modificationTime": int(datetime.now(timezone.utc).timestamp()*1000),
                    "headers": {
                        "referer": "x.com"
                    }
                })

        data = {
            "items": items,
        }

        # Send the POST request
        async with aiohttp.ClientSession() as session:
            async with session.post(f"http://{os.environ['IPv4']}:41595/api/item/addFromURLs", json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    print(result)
                    for bookmark in bookmarks:
                        if not hasattr(bookmark, 'media') or not bookmark.media:
                            if bookmark.thumbnail_url:
                                await bookmark.delete_bookmark()
                            if hasattr(bookmark, 'quote') and bookmark.quote is not None:
                                if hasattr(bookmark.quote, 'media') and bookmark.quote.media is not None:
                                    await bookmark.delete_bookmark()
                            continue
                        await bookmark.delete_bookmark()

                else:
                    print(f"Failed to post data: {response.status}")

    except Exception as error:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_no = exception_traceback.tb_lineno
        raise Exception(f"{filename}の{line_no}行目でエラーが発生しました。詳細：{error}")


if __name__ == '__main__':
    asyncio.run(main(cookie_path=sys.argv[1]))
