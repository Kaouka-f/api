import os

def createFile(file, id, filepath=''):
    ret = None
    directory_path = "/opt/files/"+filepath+id
    if not os.path.exists(directory_path):
        os.makedirs(directory_path, exist_ok=False)
    MAX_FILE_SIZE = 4 * 1024 * 1024  # 4 MB in bytes
    file_content = file.read()
    file.seek(0)
    if len(file_content) < MAX_FILE_SIZE and len(file_content) > 0:
        filename = os.path.join(directory_path, file.filename)
        file.save(filename)
        mode = os.environ.get('MODE')
        if mode == 'test':
            ret = "https://192.168.1.49/proxy/stream/"+filepath+id+'/'+file.filename
        else:
            ret = "https://elaborium.site/proxy/stream/"+filepath+id+'/'+file.filename
    else:
        print("file excedeed 4MB limit")
    return ret