from pytube import YouTube
import os

def download_video(url, download_directory):
    try:
        yt = YouTube(url)
        video_title = yt.title
        video_file_path = os.path.join(download_directory, video_title + '.mp4')

        # Check if the video file already exists
        if os.path.exists(video_file_path):
            return {"message": "Video already downloaded", "file_path": video_file_path}

        # Get the highest resolution stream
        stream = yt.streams.get_highest_resolution()

        # Download the video
        stream.download(download_directory)

        # Return the file path for the downloaded video
        return {"message": "Video downloaded successfully", "file_path": video_file_path}

    except Exception as e:
        return {"error": str(e)}


download_directory = './templates'
video_url = 'https://www.youtube.com/watch?v=Q9wWXFpb8Os'

result = download_video(video_url, download_directory)
print(result)
