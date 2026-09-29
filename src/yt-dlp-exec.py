import sys
import os
import argparse
import yt_dlp
import metadata_handler

parser = argparse.ArgumentParser()

parser.add_argument('URL', nargs='+')
parser.add_argument('-r', '--artist')
parser.add_argument('-l', '--album')
parser.add_argument('-y', '--year', type=int)
parser.add_argument('-g', '--genre', nargs='*')
parser.add_argument('-d', '--download', default=True, action=argparse.BooleanOptionalAction, help='Enable download, True by default')
parser.add_argument('-m', '--metadata', default=True, action=argparse.BooleanOptionalAction, help='Enable metadata, True by default')

HOME = os.path.expanduser('~')
# Download path
PATH = '/tmp/download/'
# Destination path
PDST = HOME + '/.local/music/'
# Temporary location of downloaded files
TEMP = PATH + 'temp/'

ydl_opts = {
    'autonumber_start': 1,
    'continue': True,
    'outtmpl': TEMP + r'%(autonumber)s-%(title)s.%(ext)s',
    'retries': 5,
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '0',
    }],
}

def main():
    args = parser.parse_args()


    if args.download:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            error_code = ydl.download([url for url in args.URL])

    if args.metadata:
        if not args.artist:
            args.artist = input("artist: ")

        if not args.album:
            args.album = input("album: ")

        if not args.year:
            args.year = int(input("year: "))

        metadata_handler.metadata_handler(args.artist, args.album, args.year, args.genre, _PATH=PATH, _PDST=PDST, _TEMP=TEMP)



if __name__ == '__main__':
    main()
else:
    print('File to be run as __main__')
