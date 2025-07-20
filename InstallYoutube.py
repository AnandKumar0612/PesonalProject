#Run pip install pytube
#Import pytube module
import pytube
from pytube import YouTube
def download_Video(link):
    if link == "":
        print("No video link to download")
    else:
        youtubeObject = pytube.YouTube(link, use_oauth=True, allow_oauth_cache=True)
        youtubeObject = youtubeObject.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').last()
        #youtubeObject = youtubeObject.streams.get_highest_resolution()
        try:
            youtubeObject.download()
        except:
            print("An error occurred in downloading")
    print("Download successfully completed")

link = input("Enter the youtube URL to download: ")
download_Video(link)