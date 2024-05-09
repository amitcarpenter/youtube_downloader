from flask import Flask,render_template, request, jsonify
from pytube import Playlist, YouTube
from pytube.exceptions import RegexMatchError
import os

app = Flask(__name__)

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




def download_video(url, file_path):
    try:
        yt = YouTube(url)
        video_title = yt.title
        video_file_path = os.path.join(file_path, video_title + '.mp4')

        # Check if the video file already exists
        if os.path.exists(video_file_path):
            return {"message": "Video already downloaded", "file_path": video_file_path}

        # Get the highest resolution stream
        stream = yt.streams.get_highest_resolution()

        # Download the video
        stream.download(file_path)

        # Return the file path for the downloaded video
        return {"message": "Video downloaded successfully", "file_path": video_file_path}

    except Exception as e:
        return {"error": str(e)}

@app.route('/api/download_video', methods=['POST'])
def api_download_video():
    try:
        data = request.json
        video_url = data.get('url')
        file_path = data.get('file_path')

        if not video_url or not file_path:
            return jsonify({"error": "Please provide both video URL and file path"})

        result = download_video(video_url, file_path)
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)})



@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
