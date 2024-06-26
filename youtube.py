

from flask import Flask, render_template, request, jsonify, send_file
from pytube import Playlist, YouTube
from pytube.exceptions import RegexMatchError
import os
from pymongo import MongoClient, errors

import threading
import re
import zipfile

# Function to connect to MongoDB
def connect_to_mongodb():
    client = MongoClient("mongodb+srv://palaksachdeva368:mzaBODxg1RKNWTaz@cluster0.xxv7t4o.mongodb.net/?retryWrites=true&w=majority/")
    db = client["job_scraping_new"]
    return db

# Function to get a collection from MongoDB
def get_collection(db, collection_name):
    return db[collection_name]

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
                    "url": yt.watch_url,
                    "streams": []
                }
                playlist_info.append(video_info)
            return jsonify(playlist_info)
        else:
            yt = YouTube(video_url)
            video_info = {
                "title": yt.title,
                "thumbnail_url": yt.thumbnail_url,
                "url": yt.watch_url,
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
        download_video(url, SAVE_DIRECTORY)
        return jsonify({'message': 'Download initiated successfully.'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download_all_video', methods=['POST'])
def download_playlist():
    try:
        data = request.json
        url = data.get('url')
        playlist = Playlist(url)
        
        # Create a folder for the playlist
        sanitized_title = re.sub(r'[<>:"/\\|?*]', '', playlist.title).replace(' ', '_')
        playlist_folder = os.path.join(SAVE_DIRECTORY, sanitized_title)
        os.makedirs(playlist_folder, exist_ok=True)
        
        # Thread management
        threads = []
        
        # Download videos into the playlist folder
        for video_url in playlist.video_urls:
            thread = threading.Thread(target=download_video, args=(video_url, playlist_folder))
            thread.start()
            threads.append(thread)
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Create zip file after all downloads are finished
        zip_filename = create_zip_from_folder(playlist_folder, sanitized_title)
        
        return jsonify({'message': 'Download initiated successfully.', 'zipUrl': f'/video/{zip_filename}'}), 200
    except Exception as e:
        print(f"Error downloading playlist: {str(e)}")
        return jsonify({'error': str(e)}), 500

def download_video(video_url, save_directory):
    try:
        yt = YouTube(video_url)
        stream = yt.streams.get_highest_resolution()
        sanitized_title = re.sub(r'[<>:"/\\|?*]', '', yt.title).replace(' ', '_')
        if not sanitized_title.endswith('.mp4'):
            sanitized_title += '.mp4'
        
        file_path = os.path.join(save_directory, sanitized_title)
        stream.download(output_path=save_directory, filename=sanitized_title)
    except Exception as e:
        print(f"Error downloading video {video_url}: {str(e)}")

def create_zip_from_folder(folder_path, zip_name):
    try:
        zip_filename = f"{zip_name}.zip"
        zip_filepath = os.path.join(SAVE_DIRECTORY, zip_filename)
        
        with zipfile.ZipFile(zip_filepath, 'w') as zipf:
            for foldername, subfolders, filenames in os.walk(folder_path):
                for filename in filenames:
                    filepath = os.path.join(foldername, filename)
                    arcname = os.path.relpath(filepath, folder_path)
                    zipf.write(filepath, arcname)
        return zip_filename
    except Exception as e:
        print(f"Error creating zip file: {str(e)}")
        raise

@app.route('/video/<filename>', methods=['GET'])
def serve_video(filename):
    video_path = os.path.join(SAVE_DIRECTORY, filename)
    if os.path.isfile(video_path):
        return send_file(video_path, as_attachment=True)
    else:
        return jsonify({'error': 'Video file not found'}), 404
    

@app.route('/jobs', methods=['GET'])
def show_jobs_html():
    db = connect_to_mongodb()
    collection = get_collection(db, "job_listings")
    jobs = list(collection.find({}, {'_id': 0}))
    return render_template('jobs.html', jobs=jobs)



if __name__ == '__main__':
    app.run(debug=True)
