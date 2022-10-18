import os
import io
from urllib import request
import requests


#dl_dir = 'testinputs'
dl_dir = './download/'
dest_dir = './xml_data/'
url = 'https://portal.cisjr.cz/pub/draha/celostatni/szdc/'
year = '2022/'
filename = 'GVD2022.zip'

class DataDownload:
    
    def __init__(self, url = url, folder = dl_dir, filaname = filename):
        self.THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
        self.url = url + year
        pass

    def download_data(self):
        if not os.path.exists(dl_dir):
            self.makedir(dl_dir)
            
        r = requests.get(url=(self.url+filename))
        if r.ok:
            print(r)
            with open(dl_dir+filename, 'wb') as f:
                f.write(r.content)
            #z = zipfile.ZipFile(io.BytesIO(r.content))
            #z.extractall(dest_dir)

    # vymaže dir
    def rmvdir(self, folder):
        os.rmdir(folder)

    # vytvorí dir
    def makedir(self, folder):
        try:
            if not os.path.isdir(folder):
                oldmask = os.umask(000)
                os.makedirs(folder, 0o777)
                os.umask(oldmask)
            os.chmod(folder, 0o777)
        except FileNotFoundError:
            print("FileNotFoundError error")
            exit(0)
            

def main():
    test = DataDownload()
    test.download_data()

if __name__ == "__main__":
    main()