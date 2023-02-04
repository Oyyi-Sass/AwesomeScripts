import os
import requests
import fire
import wget

PEXEL_URL = "https://api.pexels.com/videos/search?"
PEXEL_API_KEY = None


def getRandomVideo(query, count, page, orientation, resolution):
    print(f"Fetching Page {page}")
    compareBy = "height" if orientation == "landscape" else "width"
    downloaded = []
    video_urls = []
    search_url = f"{PEXEL_URL}query={query}&page={page}" \
                 f"&per_page={count}&size=large&orientation={orientation}"
    r = requests.get(search_url, headers={f"Authorization": f"Bearer {PEXEL_API_KEY}"})
    if r.status_code != 200:
        raise Exception("Unable to get video due to " + r.text)
    videos = r.json()["videos"]
    for video in videos:
        if video[compareBy] >= resolution and str(video["id"]) not in downloaded:
            downloaded.append(str(video["id"]))
            for link in video["video_files"]:
                if (link[compareBy] - resolution) <= 100:
                    video_urls.append(link["link"])
                    break
    return video_urls


def bulkVideoFetch(query: str, count: int, batch: int = 50, orientation="landscape", resolution=2160):
    total_batch = count // batch
    remaining = count % batch
    video_urls = []
    for i in range(1, total_batch + 1):
        video_urls = video_urls + getRandomVideo(query, count=batch, page=i, resolution=resolution,
                                                 orientation=orientation)
    if remaining > 0:
        video_urls = video_urls + getRandomVideo(query, count=remaining, page=total_batch + 1, resolution=resolution,
                                                 orientation=orientation)
    return set(video_urls)


def run(topic, key: str, count: int = 10, location: str = "download", resolution: str = "720p",
        orientation="landscape"):
    topic = topic if isinstance(topic, tuple) else [topic]
    res = {
        "480p": (640, 480),
        "720p": (1280, 720),
        "1080p": (1920, 1080),
        "2k": (2560, 1440),
        "4k": (3840, 2160),
    }
    global PEXEL_API_KEY
    PEXEL_API_KEY=key
    if resolution not in res:
        raise Exception("Unsupported resolution. Only 480p,720p,1080p,2k,4k")
    if orientation not in ("landscape", "portrait"):
        raise Exception("Invalid Orientation. Allowed landscape, portrait")
    resolution = res[resolution][1]
    os.makedirs(f"{location}", exist_ok=True)
    for t in topic:
        print(f"Getting Video for topic {t}")
        urls = list(bulkVideoFetch(t, count=count, resolution=resolution, orientation=orientation))
        print(f"Starting File Download for topic {t}")
        os.makedirs(f"{location}/{t}", exist_ok=True)
        for i in range(len(urls)):
            try:
                print(f"Downloading File {i}")
                wget.download(urls[i], out=f"{location}/{t}")
                print("\n")
            except Exception as e:
                print(e)


if __name__ == '__main__':
    fire.Fire(run)
