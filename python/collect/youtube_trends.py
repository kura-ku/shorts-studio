import yt_dlp
import pandas as pd
from datetime import datetime
from pathlib import Path
import time

# ============================================
# 設定
# ============================================

SEARCH_GROUPS = {

    "mindset": [
        "mindset shorts",
        "focus shorts",
        "self improvement shorts",
        "discipline shorts",
        "deep work shorts"
    ],

    "emotion": [
        "anxiety shorts",
        "overthinking shorts",
        "mental reset shorts",
        "burnout shorts",
        "loneliness shorts"
    ],

    "ai_future": [
        "AI future shorts",
        "AI jobs shorts",
        "automation shorts",
        "AI productivity shorts",
        "future of work shorts"
    ]
}

MAX_RESULTS_PER_QUERY = 10

OUTPUT_DIR = Path("data/trends")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "youtube_trends.csv"

# ============================================
# yt-dlp 設定
# ============================================

YDL_OPTS = {

    "extract_flat": True,

    "quiet": True,

    "skip_download": True,

    "nocheckcertificate": True,

    "ignoreerrors": True
}

# ============================================
# データ格納
# ============================================

all_rows = []

# ============================================
# メイン処理
# ============================================

print("=" * 50)
print("YouTube Shorts Trend Collector")
print("=" * 50)

with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:

    for category, queries in SEARCH_GROUPS.items():

        print(f"\nCATEGORY: {category}")

        for query in queries:

            print(f"\nSEARCH: {query}")

            search_url = (
                "https://www.youtube.com/results?"
                f"search_query={query}"
            )

            try:

                # --------------------------------
                # 検索結果取得
                # --------------------------------

                result = ydl.extract_info(
                    search_url,
                    download=False
                )

                if not result:
                    print("No result")
                    continue

                entries = result.get("entries", [])

                if not entries:
                    print("No entries")
                    continue

                # --------------------------------
                # 各動画処理
                # --------------------------------

                for entry in entries[:MAX_RESULTS_PER_QUERY]:

                    try:

                        video_id = entry.get("id")

                        if not video_id:
                            continue

                        video_url = (
                            f"https://www.youtube.com/watch?"
                            f"v={video_id}"
                        )

                        print(f"Checking: {video_id}")

                        # --------------------------------
                        # 動画詳細取得
                        # --------------------------------

                        detail = ydl.extract_info(
                            video_url,
                            download=False
                        )

                        if not detail:
                            continue

                        duration = detail.get("duration")

                        # --------------------------------
                        # Shorts判定
                        # --------------------------------

                        if duration is None:
                            continue

                        if duration > 60:
                            print("Skip: not shorts")
                            continue

                        # --------------------------------
                        # データ作成
                        # --------------------------------

                        row = {

                            "collected_at":
                                datetime.now().strftime(
                                    "%Y-%m-%d %H:%M:%S"
                                ),

                            "category":
                                category,

                            "query":
                                query,

                            "title":
                                detail.get("title"),

                            "video_id":
                                video_id,

                            "video_url":
                                video_url,

                            "channel":
                                detail.get("channel"),

                            "channel_id":
                                detail.get("channel_id"),

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

                            "description":
                                detail.get("description"),

                            "tags":
                                ",".join(
                                    detail.get("tags", [])
                                )
                                if detail.get("tags")
                                else "",

                            "language":
                                detail.get("language"),

                            "availability":
                                detail.get("availability")

                        }

                        all_rows.append(row)

                        print(
                            f"OK: "
                            f"{row['title'][:50]}"
                        )

                        # --------------------------------
                        # 負荷軽減
                        # --------------------------------

                        time.sleep(1)

                    except Exception as e:

                        print(
                            f"DETAIL ERROR: {e}"
                        )

            except Exception as e:

                print(
                    f"SEARCH ERROR: {e}"
                )

# ============================================
# DataFrame化
# ============================================

df = pd.DataFrame(all_rows)

# ============================================
# 重複削除
# ============================================

if not df.empty:

    df.drop_duplicates(
        subset=[
            "video_id"
        ],
        inplace=True
    )

# ============================================
# ソート
# ============================================

if "views" in df.columns:

    df = df.sort_values(
        by="views",
        ascending=False
    )

# ============================================
# CSV保存
# ============================================

df.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig"
)

# ============================================
# 完了表示
# ============================================

print("\n" + "=" * 50)
print("COLLECT FINISHED")
print("=" * 50)

print(f"Saved File: {OUTPUT_FILE}")

print(f"Total Videos: {len(df)}")

print("=" * 50)
