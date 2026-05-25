```python
import yt_dlp
import pandas as pd
from datetime import datetime
from pathlib import Path
import time
import random

# ==================================================
# 設定
# ==================================================

# 検索カテゴリ
SEARCH_GROUPS = {

    "mindset": [
        "mindset shorts",
        "focus shorts",
        "discipline shorts"
    ],

    "emotion": [
        "anxiety shorts",
        "overthinking shorts",
        "burnout shorts"
    ],

    "ai_future": [
        "AI future shorts",
        "AI jobs shorts",
        "automation shorts"
    ]
}

# 検索数（最初は少なく）
MAX_RESULTS_PER_QUERY = 3

# 出力先
OUTPUT_DIR = Path("data/trends")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "youtube_trends.csv"

# ==================================================
# yt-dlp 設定
# ==================================================

YDL_OPTS = {

    # ログ表示
    "quiet": False,

    # ダウンロードしない
    "skip_download": True,

    # エラー無視
    "ignoreerrors": True,

    # SSL
    "nocheckcertificate": True,

    # フラット取得
    "extract_flat": True,

    # Bot対策
    "sleep_interval": 2,
    "max_sleep_interval": 5,

    # Chrome Cookie利用
    # Chromeログイン状態を使う
    "cookiesfrombrowser": ("chrome",),

    # UserAgent
    "http_headers": {
        "User-Agent":
        (
            "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/124.0 Safari/537.36"
        )
    }
}

# ==================================================
# データ保存
# ==================================================

all_rows = []

# ==================================================
# メイン
# ==================================================

print("=" * 60)
print("YouTube Shorts Trend Collector")
print("=" * 60)

with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:

    # ----------------------------------------------
    # カテゴリループ
    # ----------------------------------------------

    for category, queries in SEARCH_GROUPS.items():

        print(f"\nCATEGORY: {category}")

        # ------------------------------------------
        # 検索ワードループ
        # ------------------------------------------

        for query in queries:

            print(f"\nSEARCH: {query}")

            # --------------------------------------
            # ytsearch方式へ変更
            # Bot判定回避
            # --------------------------------------

            search_query = (
                f"ytsearch{MAX_RESULTS_PER_QUERY}:{query}"
            )

            try:

                result = ydl.extract_info(
                    search_query,
                    download=False
                )

                if not result:
                    print("No Result")
                    continue

                entries = result.get("entries", [])

                if not entries:
                    print("No Entries")
                    continue

                # ----------------------------------
                # 動画処理
                # ----------------------------------

                for entry in entries:

                    try:

                        if not entry:
                            continue

                        video_id = entry.get("id")

                        if not video_id:
                            continue

                        video_url = (
                            f"https://www.youtube.com/watch?"
                            f"v={video_id}"
                        )

                        print(f"\nChecking: {video_id}")

                        # --------------------------
                        # 詳細取得
                        # --------------------------

                        detail = ydl.extract_info(
                            video_url,
                            download=False
                        )

                        if not detail:
                            continue

                        # --------------------------
                        # Shorts判定
                        # --------------------------

                        duration = detail.get("duration")

                        if duration is None:
                            print("Skip: duration none")
                            continue

                        if duration > 60:

                            print(
                                f"Skip Long Video: "
                                f"{duration}s"
                            )

                            continue

                        # --------------------------
                        # データ生成
                        # --------------------------

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
                            f"{row['title'][:60]}"
                        )

                        # --------------------------
                        # ランダムsleep
                        # --------------------------

                        sleep_time = random.randint(3, 7)

                        print(
                            f"sleep: {sleep_time}s"
                        )

                        time.sleep(sleep_time)

                    except Exception as e:

                        print(
                            f"DETAIL ERROR: {e}"
                        )

                        continue

            except Exception as e:

                print(
                    f"SEARCH ERROR: {e}"
                )

                continue

# ==================================================
# DataFrame化
# ==================================================

df = pd.DataFrame(all_rows)

# ==================================================
# 重複削除
# ==================================================

if not df.empty:

    df.drop_duplicates(
        subset=["video_id"],
        inplace=True
    )

# ==================================================
# viewsソート
# ==================================================

if "views" in df.columns:

    df = df.sort_values(
        by="views",
        ascending=False
    )

# ==================================================
# CSV保存
# ==================================================

df.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig"
)

# ==================================================
# 完了
# ==================================================

print("\n" + "=" * 60)
print("COLLECT FINISHED")
print("=" * 60)

print(f"Saved File : {OUTPUT_FILE}")
print(f"Total Videos: {len(df)}")

print("=" * 60)
```
