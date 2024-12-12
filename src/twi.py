import sys
import asyncio

from bookmark2eagle import bookmark2eagle

if __name__ == "__main__":
    asyncio.run(bookmark2eagle(cookie_path=sys.argv[1]))
