import yt_dlp
import pandas as pd
from datetime import datetime
from pathlib import Path

# =========================
# 設定
# =========================

SEARCH_GROUPS = {

    "mindset": [
        "mindset shorts",
        "focus shorts",
        "self improvement shorts"
    ],

    "emotion": [
        "anxiety shorts",
        "overthinking shorts",
        "mental reset shorts"
    ],

    "ai_future": [
        "AI future shorts",
        "AI jobs shorts",
        "automation shorts"
    ]
}

MAX_RESULTS = 10

OUTPUT_DIR = Path("data/trends")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "youtube_trends.csv"

# =========================
# yt-dlp 設定
# =========================

ydl_opts = {
    "extract_flat": True,
    "quiet": True,
    "skip_download": True
}

all_data = []

# =========================
# メイン処理
# =========================

with yt_dlp.YoutubeDL(ydl_opts) as ydl:

    for category, queries in SEARCH_GROUPS.items():

        print(f"\n=== CATEGORY: {category} ===")

        for query in queries:

            print(f"search: {query}")

            search_url = (
                "https://www.youtube.com/results?"
                f"search_query={query}"
            )

            try:

                result = ydl.extract_info(
                    search_url,
                    download=False
                )

                entries = result.get("entries", [])

                for entry in entries[:MAX_RESULTS]:

                    try:

                        video_id = entry.get("id")

                        if not video_id:
                            continue

                        video_url = (
                            f"https://www.youtube.com/watch?v={video_id}"
                        )

                        # 詳細取得
                        detail = ydl.extract_info(
                            video_url,
                            download=False
                        )

                        duration = detail.get("duration")

                        # Shorts判定
                        if duration and duration > 60:
                            continue

                        row = {

                            "timestamp":
                                datetime.now(),

                            "category":
                                category,

                            "query":
                                query,

                            "title":
                                detail.get("title"),

                            "video_id":
                                video_id,

                            "channel":
                                detail.get("channel"),

                            "views":
                                detail.get("view_count"),

                            "likes":
                                detail.get("like_count"),

                            "comments":
                                detail.get("comment_count"),

                            "duration":
                                duration,

                            "upload_date":
                                detail.get("upload_date"),

                            "url":
                                video_url

                        }

                        all_data.append(row)

                        print(
                            f"OK: {row['title']}"
                        )

                    except Exception as e:

                        print(
                            f"detail error: {e}"
                        )

            except Exception as e:

                print(
                    f"search error: {e}"
                )

# =========================
# CSV保存
# =========================

df = pd.DataFrame(all_data)

df.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig"
)

print("\nDONE")
print(f"saved: {OUTPUT_FILE}")
