__author__ = 'sabbana'

# This application was purposed to downloaded file from google Drive.
# 
# @used
#     python gdrive_downloader.py [ gid ] [ destination ]
# @ex
#     python gdrive_downloader.py "1mv7ryvScjmJ50XZSlmYZytfAr6n9_gMy" "/home/data/file.mp4"
#     [ or ]
#     python gdrive_downloader.py "1mv7ryvScjmJ50XZSlmYZytfAr6n9_gMy" "/home/data/file"
#
#     sample gfile url : https://drive.google.com/open?id=1mv7ryvScjmJ50XZSlmYZytfAr6n9_gMy
#     

import requests, sys, json, datetime

apikey = GOOGLE_API_KEY #please put your google api key here
allowed_type = ['mp4','mov','mpeg','avi','jpg','jpeg','png']

def get_file_attr(id):
    URL = "https://www.googleapis.com/drive/v3/files/"+str(id)+"?key="+str(apikey)+"&fields=size,mimeType"
    response = requests.get(URL)
    res = json.loads(response.text)
    if 'error' not in res:
        if 'size' in res:
            return res
    return None

def download_file_from_google_drive(id, destination):
    URL = "https://docs.google.com/uc?export=download"
    session = requests.Session()
    response = session.get(URL, params = { 'id' : id }, stream = True)
    if response.status_code == 404 :
        print ("Error, File id not found or it is private file. Please set public to allow access")
        return False

    token = get_confirm_token(response)
    if token:
        params = { 'id' : id, 'confirm' : token }
        response = session.get(URL, params = params, stream = True)
    save_response_content(response, destination)

def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value
    return None

def save_response_content(response, destination):
    global _gid, _dest
    _attr = get_file_attr(_gid)
    ext = _attr['mimeType'].split('/')[1]
    
    # force extension file from quictime and x-msvideo mime
    if ext == 'quicktime': ext = 'mov'
    if ext == 'x-msvideo': ext = 'avi'
    if ext not in allowed_type:
        print ("Error, Filetype not allowed!")
        return False

    print (str(datetime.datetime.now())[:19]+" Fetching file "+str(_gid)+"...")

    _destination = destination
    if destination.find('.') == -1 :
        _destination = destination+'.'+ext
    else: _destination = destination.split('.')[0]+'.'+ext

    filesize = float(_attr['size'])/(1000*1000)
    CHUNK_SIZE = 1*1000 #0.1MB

    with open(_destination, "wb") as f:
        percent = 0
        dl = 0
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
                dl += len(chunk)
                _download = float(dl)/(1000*1000)
                percent = 100*(float(_download)/float(filesize))
                sys.stdout.write("Downloading : %4.2f MB [ %d%s ]  \r" % (_download, int(percent), '%') )
                sys.stdout.flush()
        if percent == 100:
            print (str(datetime.datetime.now())[:19]+" Downloaded! "+str(_download)+" MB")
            
    return "OK"
    

# argv global variable
# google drive id , destination_file
def argv():
    global _gid, _dest
    if len(sys.argv) < 3:
        _help()
        return False
    _gid = sys.argv[1];
    _dest = sys.argv[2]; 
#,-

def _help():
    print ("NAME")
    print ("    gdrive_downloader.py")
    print ("")
    print ("SYNOPSIS")
    print ("    how to use")
    print ("    python gdrive_downloader.py [ gid ] [ destination_file ]")
    print ("")
    print ("    ex:")
    print ("    python gdrive_downloader.py UCdzAmLcdR5R5W-r1xudnbRQ /home/data/filename.mp4")
    print ("")
    print ("DESCRIPTION")
    print ("    gdrive_downloader.py -- download file from google drive")
    print ("    gid, represent google drive file id. You can discover from 'get sharable link'")
    print ("    destination_file, represent destination file where you will store the file in local storage")
    print ("")
    exit()
#,--

if __name__ == "__main__":
    global _gid, _dest
    argv()
    download_file_from_google_drive(_gid, _dest)
