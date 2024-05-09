from flask import Flask,render_template, request, jsonify
from pytube import Playlist, YouTube
from pytube.exceptions import RegexMatchError
import os
import threading
import re

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/get_video_info', methods=['POST'])
def get_video_info():
    try:
        video_url = request.json.get('url')
        if 'list' in video_url.lower():
            playlist = Playlist(video_url)
            playlist_info = []
            for video in playlist.video_urls:
                yt = YouTube(video)
                video_info = {
                    "title": yt.title,
                    "thumbnail_url": yt.thumbnail_url,
                    "url" : yt.watch_url,
                    "streams": []
                }
                print(video_info)
                playlist_info.append(video_info)
            return jsonify(playlist_info)

        else:
            print("hello")
            yt = YouTube(video_url)
            print(vars(yt))
            video_info = {
                "title": yt.title,
                "thumbnail_url": yt.thumbnail_url,
                "url" : yt.watch_url,
                "streams": []
            }
            return jsonify([video_info])

    except Exception as e:
        return jsonify({"error": str(e)})


SAVE_DIRECTORY = "./videos/"


@app.route('/api/download_video', methods=['POST'])
def download_from_url():
    data = request.json
    url = data.get('url')
    try:
        if 'list' in url:
            download_playlist(url)
        else:
            download_video(url)
        return jsonify({'message': 'Download initiated successfully.'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500



def download_playlist(playlist_url):
    playlist = Playlist(playlist_url)
    for video_url in playlist.video_urls:
        threading.Thread(target=download_video, args=(video_url,)).start()


def download_video(video_url):
    try:
        yt = YouTube(video_url)
        stream = yt.streams.get_highest_resolution()
        sanitized_title = re.sub(r'[<>:"/\\|?*]', '', yt.title)
        sanitized_title = sanitized_title.replace(' ', '_') 
        if not sanitized_title.endswith('.mp4'):
            sanitized_title += '.mp4'
        print("Sanitized title:", sanitized_title)

        file_path = os.path.join(SAVE_DIRECTORY, sanitized_title)
        stream.download(output_path=SAVE_DIRECTORY, filename=sanitized_title)
    except Exception as e:
        print("Error:", e)



if __name__ == '__main__':
    app.run(debug=True)
