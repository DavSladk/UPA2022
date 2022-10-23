import os
import io
from select import select
from time import process_time_ns
from traceback import print_tb
import requests
import re
import shutil
import gzip


from bs4 import BeautifulSoup
import zipfile

#dl_dir = 'testinputs'
dl_dir = 'zips/'
dest_dir = 'xml_data/'
url_base = 'https://portal.cisjr.cz'
url = 'https://portal.cisjr.cz/pub/draha/celostatni/szdc/2022'
year = '2022/'
filename = 'GVD2022.zip'

pattern = '[0-9]{4}-[0-9]{2}'


class DataDownload:
    
    url = url
    links = []
    GVDzip = []
    zips = []


    def __init__(self):
        self.THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
        pass

    def download_GVD(self):
        # Creates zips/ dir
        if not os.path.exists(dl_dir):
            self.makedir(dl_dir)

        # Gets gvd zip from https://portal.cisjr.cz/pub/draha/celostatni/szdc/2022/
        html = requests.get(url)
        soup = BeautifulSoup(html.text, features="html.parser")
        for a in soup.findAll('a', href=True):
            if re.search('.zip$', a['href']):
                self.GVDzip.append(url_base + a['href'])


        # Downloads zip files
        for zip in self.GVDzip:
            zip_file = re.split(r'[\/]', zip)[-1]

            path = dl_dir + '/' + zip_file
            if not os.path.exists(path):
                r = requests.get(zip)
                if r.ok:
                    with open(path, 'wb') as f:
                        f.write(r.content)


    def download_zips(self):
        # Creates zips/ dir
        if not os.path.exists(dl_dir):
            self.makedir(dl_dir)
        
        self.download_GVD()

        # Gets links from https://portal.cisjr.cz/pub/draha/celostatni/szdc/2022/ 
        html = requests.get(url)
        soup = BeautifulSoup(html.text, features="html.parser")
        for a in soup.findAll('a', href=True):
            if re.search(pattern, a['href']):
                self.links.append(url_base + a['href'])
        
        # Goes through links (Jan-Dec)
        for link in self.links:
            print(link)
            html = requests.get(link)
            soup = BeautifulSoup(html.text, features="html.parser")
            for a in soup.findAll('a', href=True):
                if re.search('.zip$', a['href']):
                    self.zips.append(url_base + a['href'])
            #break # comment for one month, else full year

        # Downloads every zip (Jan-Dec)
        test = 0
        for zip in self.zips:
            zip_file = re.split(r'[\/]', zip)[-1]
            zip_year = re.split(r'[\/]', zip)[-2]
            
            # DOWNLOAD ONLY FIRST 30 (TEST)
            #if test == 30:
            #    return
            #test += 1

            if not os.path.exists(dl_dir + zip_year):
                self.makedir(dl_dir + zip_year)

            path = os.path.join(dl_dir + zip_year + '/' + zip_file)
            if not os.path.exists(path):
                r = requests.get(zip)
                if r.ok:
                    with open(path, 'wb') as f:
                        f.write(r.content)



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
    
    def clear(self):
        if os.path.exists(dl_dir):
            shutil.rmtree(dl_dir)
            

class DataExtract:

    # Makes dir
    @staticmethod
    def makedir(folder):
        try:
            if not os.path.isdir(folder):
                oldmask = os.umask(000)
                os.makedirs(folder, 0o777)
                os.umask(oldmask)
            os.chmod(folder, 0o777)
        except FileNotFoundError:
            print("FileNotFoundError error")
            exit(0)

    def extract_all(months, GVD):
        DataExtract.makedir(dest_dir)
        if (months):
             for root, dirs, files in os.walk(dl_dir):
                for filename in files:
                    print("Extracting: ",filename)
                    # Zips without GVD batches
                    if re.search(r'\.zip$', filename) and not re.search(r'^GVD', filename):

                        # ZIP
                        if zipfile.is_zipfile(root + '/' + filename):
                            unzip = zipfile.ZipFile(root + '/' + filename, 'r', allowZip64=True)
                            unzip.extractall(dest_dir)
                            unzip.close() 

                        # GZIP
                        else:
                            f = gzip.open(root + '/' + filename, 'r')
                            s = f.read()
                            f.close()
                            output = open(dest_dir + filename[:-4], 'wb')
                            output.write(s)
                            output.close

        if (GVD):
            zipfiles = [f for f in os.listdir(dl_dir) if f.endswith(".zip")]
            for zip in zipfiles:
                unzip = zipfile.ZipFile(dl_dir + zip, 'r')
                unzip.extractall(dest_dir)
                unzip.close()

    # Deletes XML folder
    def clear():
        if os.path.exists(dest_dir):
            shutil.rmtree(dest_dir)


def main():
    test = DataDownload()
    test.download_zips()
    DataExtract.clear()
    #GVD consists of GVD2022-oprava_poznamek_KJR_vybranych_tras20220126.zip and GVD2022.zip
    DataExtract.extract_all(months=True, GVD=True)

if __name__ == "__main__":
    main()