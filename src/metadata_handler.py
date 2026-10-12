import os
import shutil
import eyed3
import mutagen
import codecs
import re

HOME = os.path.expanduser('~')
# Download path
PATH = '/tmp/download/'
# Destination path
PDST = HOME + '/.local/music/'
# Temporary location of downloaded files
TEMP = PATH + 'temp/'

CLR_NAME = False

# Find the folder where the files are to be moved to after tagging
# Folder is named in form of: {artist_name} - {album_title}
def defineAlbumPath(_input=None):
    # Album name passed as argument
    if _input:
        return {'full_title':_input, 'album_dir':PATH + _input}
    else:
        DIRS = [n for n in os.listdir(PATH)]
        for n in DIRS:
            if n != 'temp':
                albm = n
                albm_dir = PATH + n
                return {'full_title':albm, 'album_dir':albm_dir}

# Make a list of *.mp3 files in the PATH/temp/ (folder used for storing downloaded files)
def getFilesInTemp():
    file_names = [n for n in os.listdir(TEMP) if os.path.isfile(os.path.join(TEMP, n)) and os.path.splitext(n)[1] == '.mp3']
    return(sorted(file_names))

def looseFileMove(albm_dir, album):
    if not os.path.exists(albm_dir):
        return;

    file_names = [n for n in os.listdir(albm_dir) if os.path(os.path.join(albm_dir, n))]
    for file in file_names:
        src = albm_dir + file
        dst = PDST + album + '/' + file
        shutil.move(src, dst)

def getGenInfo(albm, _year=None, _genre=None):
    gen_data = {'artist_name':None, 'album_title':None, 'year':None,  'genre':None}
    #'- ' changed to ' - ' to cover cases of hyphen in artist name
    gen_data['artist_name'] = albm[:(albm.index(' - '))]
    # 3 is used to remove ' - ' starting at the first blank space
    gen_data['album_title'] = albm[(albm.index(' - ') + 3):]
    # TODO query the web to find album release date?
    gen_data['year'] = _year if _year else str(input("Release year: "))
    gen_data['genre'] = ';'.join(_genre) if _genre else str(input("Genre: "))
    return(gen_data)

def clearName(file_name):
    # Remove the numbering in front of the name and rename the file
    full_name = os.path.splitext(file_name[(file_name.index('-') + 1):])
    # Clear any informative text at the end of the file name
    name = re.sub(r'\s*\((?=[^)]*[A-Za-z])(?:[^()]|\([^()]*\))*\)\s*$', '', full_name[0]) if CLR_NAME else full_name[0]
    shutil.move(TEMP + file_name, TEMP + name + full_name[1])
    return name

def getNameAndIndex(file_name):
    # Downloaded file names formed as XXXXX-{song_name}
    index = int(file_name[:(file_name.index('-'))])
    name = clearName(file_name)
    return {'song_name':name, 'index':index}

def moveFile(file_name, album):
    scr = TEMP + file_name + '.mp3'
    dst = PDST + album + '/' + file_name + '.mp3'
    shutil.move(scr, dst)

def getRuntime(file):
    audio = mutagen.File(file)
    return(audio.info.length)
 
def m3u8Editor(m3u8File, playlist):
    line = f"#EXTINF:{playlist[2]}, {playlist[0]} - {playlist[1]}\n{playlist[1]}.mp3\n"
    m3u8File.writelines(line)


def metadata_handler(_artist=None, _albm=None, _year=None, _genre=None, _PATH=None, _PDST=None, _TEMP=None, _CLR_NAME=None):
    if _PATH:
        global PATH
        PATH = _PATH

    if _PDST:
        global PDST
        PDST = _PDST

    if _TEMP:
        global TEMP
        TEMP = _TEMP

    if _CLR_NAME:
        global CLR_NAME
        CLR_NAME = _CLR_NAME

    if not os.path.exists(PDST):
        os.mkdir(PDST)

    albm_info = defineAlbumPath(_artist + ' - ' +_albm if _artist and _albm 
                                else None)
    down_list = getFilesInTemp()
    # General metadata the is used immutably for every file
    gen_data = getGenInfo(albm_info['full_title'], _year, _genre)
    # Make a new directory to hold tagged files
    fpath = PDST + albm_info['full_title']

    if albm_info['full_title'] not in os.listdir(PDST): 
        os.mkdir(fpath)

    m3u8Path = os.path.join(fpath, "{}.m3u8".format(
        os.path.basename(fpath)
    ))

    with codecs.open(m3u8Path, "w", "utf-8") as m3u8File:
        m3u8File.writelines("#EXTM3U\n")

        playlist = []

        for file_name in down_list:
            # Get file name and index for every separate file
            index_data = getNameAndIndex(file_name)
            audfile = eyed3.load(TEMP + index_data['song_name'] + '.mp3')
            print('Editing metadata of '+ index_data['song_name'] + '...')
            # Edit the following metadata tags
            audfile.tag.artist = gen_data['artist_name']
            audfile.tag.album_artist = gen_data['artist_name']
            audfile.tag.album = gen_data['album_title']
            audfile.tag.title = index_data['song_name']
            audfile.tag.track_num = index_data['index']
            audfile.tag.recording_date = gen_data['year']
            audfile.tag.genre = gen_data['genre']
            # Save changed tags
            audfile.tag.save()

            # Get info for m3u8 file
            playlist.append(gen_data['artist_name'])
            playlist.append(index_data['song_name'])
            playlist.append(getRuntime(TEMP + index_data['song_name'] + '.mp3'))

            print(f'Editing "{gen_data['artist_name']} - {gen_data['album_title']}.m3u8"')
            m3u8Editor(m3u8File, playlist)

            playlist = []

            print('Moving ' + index_data['song_name'] + '...')
            moveFile(index_data['song_name'], albm_info['full_title'])

        m3u8File.close()

    # Check to see if any loose files(i.e. album cover) are still in the original album directory and move them
    looseFileMove(albm_info['album_dir'], albm_info['full_title'])
    
    print('Done')

    # Delete the now empty dir in PATH
    if os.path.exists(albm_info['album_dir']):
        os.rmdir(albm_info['album_dir'])

def main():
    metadata_handler(sys.argv[1] if len(sys.argv) > 1 else None,
                     sys.argv[2] if len(sys.argv) > 2 else None,
                     sys.argv[3] if len(sys.argv) > 3 else None)

if __name__ == '__main__':
    main()
