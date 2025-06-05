import asyncio
import os
from app.stream import get_stream_url, open_stream
from app.websocket_server import start_websocket_server
from app.analysis import analyze_every_interval, BG_HIVE1_STATIC, BG_HIVE23_STATIC
from dotenv import load_dotenv
load_dotenv()


async def main():
    stream_url_1 = get_stream_url(os.getenv("YOUTUBE_URL_1"))
    stream_url_2 = get_stream_url(os.getenv("YOUTUBE_URL_2"))
    cap1 = open_stream(stream_url_1)
    cap2 = open_stream(stream_url_2)

    await asyncio.gather(
        start_websocket_server(),
        analyze_every_interval(cap1, ["Hive_1"], BG_HIVE1_STATIC),
        analyze_every_interval(cap2, ["Hive_2", "Hive_3"], BG_HIVE23_STATIC),
    )

if __name__ == "__main__":
    asyncio.run(main())
