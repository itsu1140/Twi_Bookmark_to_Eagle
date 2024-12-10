import os
import sys
import errno
import aiohttp
import asyncio
import tkinter as tk
from tkinter import filedialog
from twikit import Client
from datetime import datetime, timezone

# Default number of tweets
twi_num = 30


async def main(cookie_path, twi_num):
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
            if not hasattr(bookmark, "media") or not bookmark.media:
                if bookmark.thumbnail_url:
                    items.append(
                        {
                            "url": bookmark.thumbnail_url,
                            "name": f"@{bookmark.user.screen_name} {bookmark.text}",
                            "website": f"https://x.com/{bookmark.user.screen_name}/status/{bookmark.id}/",
                            "tags": [],
                            "modificationTime": int(
                                datetime.now(timezone.utc).timestamp() * 1000
                            ),
                            "headers": {"referer": "x.com"},
                        }
                    )
                if (
                    hasattr(bookmark, "quote")
                    and bookmark.quote is not None
                    and hasattr(bookmark.quote, "media")
                    and bookmark.quote.media is not None
                ):
                    items.append(
                        {
                            "url": bookmark.quote.media[0].get("media_url_https"),
                            "name": f"@{bookmark.quote.user.screen_name} {bookmark.quote.text}",
                            "website": f"https://x.com/{bookmark.quote.user.screen_name}/status/{bookmark.quote.id}/",
                            "tags": [],
                            "modificationTime": int(
                                datetime.now(timezone.utc).timestamp() * 1000
                            ),
                            "headers": {"referer": "x.com"},
                        }
                    )
                continue
            for media in bookmark.media:
                items.append(
                    {
                        "url": media.get("media_url_https"),
                        "name": f"@{bookmark.user.screen_name} {bookmark.text}",
                        "website": f"https://x.com/{bookmark.user.screen_name}/status/{bookmark.id}/",
                        "tags": [],
                        "modificationTime": int(
                            datetime.now(timezone.utc).timestamp() * 1000
                        ),
                        "headers": {"referer": "x.com"},
                    }
                )

        data = {
            "items": items,
        }

        # Send the POST request
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "http://127.0.0.1:41595/api/item/addFromURLs", json=data
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    print(result)
                    for bookmark in bookmarks:
                        if not hasattr(bookmark, "media") or not bookmark.media:
                            if bookmark.thumbnail_url:
                                await bookmark.delete_bookmark()
                            if (
                                hasattr(bookmark, "quote")
                                and bookmark.quote is not None
                            ):
                                if (
                                    hasattr(bookmark.quote, "media")
                                    and bookmark.quote.media is not None
                                ):
                                    await bookmark.delete_bookmark()
                            continue
                        await bookmark.delete_bookmark()
                else:
                    print(f"Failed to post data: {response.status}")

    except Exception as error:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_no = exception_traceback.tb_lineno
        raise Exception(
            f"{filename}の{line_no}行目でエラーが発生しました。詳細：{error}"
        )


def run_main():
    cookie_path = cookie_path_var.get()
    twi_num = twi_num_var.get()
    asyncio.run(main(cookie_path, twi_num))


def select_cookie_file():
    file_path = filedialog.askopenfilename()
    cookie_path_var.set(file_path)


# Create the main window
root = tk.Tk()
root.title("Twitter Bookmark Manager")

# Cookie path entry
cookie_path_var = tk.StringVar()
cookie_path_label = tk.Label(root, text="Cookieファイルの場所:")
cookie_path_label.pack()
cookie_path_entry = tk.Entry(root, textvariable=cookie_path_var, width=50)
cookie_path_entry.pack()
cookie_path_button = tk.Button(
    root, text="Cookieファイルを選ぶ", command=select_cookie_file
)
cookie_path_button.pack()

# Tweet number slider
twi_num_var = tk.IntVar(value=twi_num)
twi_num_label = tk.Label(root, text="チェックするBookmarkの数(レート制限注意):")
twi_num_label.pack()
twi_num_slider = tk.Scale(
    root, from_=1, to=100, orient=tk.HORIZONTAL, variable=twi_num_var
)
twi_num_slider.pack()

# Run button
run_button = tk.Button(root, text="実行", command=run_main)
run_button.pack()

# Start the GUI event loop
root.mainloop()
