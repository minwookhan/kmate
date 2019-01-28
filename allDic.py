from bs4 import BeautifulSoup
from PIL import Image
import urllib.request, re
from urllib.request import urlopen, urlretrieve

#ImageFile.LOAD_TRUNCATED_IMAGES = True
import sys , time , os
class ldoce_dn:
    def __init__(self):
        pass
    def _reporthook_(self, count, block_size, total_size):

        global start_time
        if count == 0:
            start_time = time.time()
            return
        duration = time.time() - start_time
        progress_size= int(count * block_size)
        speed = int(progress_size / (1024 * duration))
        percent = int(count * block_size * 100 / total_size)
        sys.stdout.write("\r...%d%%, %.2f MB, %d KB/s, %d seconds passed" %
                        (percent, progress_size / (1024 * 1024), speed, duration))
        sys.stdout.flush()


    def save(self, url, path_filename):
        print('{} is downloading '.format(path_filename))
        try:
            urlretrieve(url, path_filename, self._reporthook_)
        except Exception:
            return ''
            #raise Exception("urlretrieve Error")


class All_Dic(BeautifulSoup):
    def __init__(self, _dic_name, _dic=0):

        self.DIC_NAME =  _dic_name 
        self.WORD = 'a'
        self._dic_num = _dic
        if _dic_name.lower() in ['ldoce', 'longman']:
            self.baseURL = 'https://www.ldoceonline.com/dictionary'
            self.DICS = ['From Longman Dictionary of Contemporary English','From Longman Business Dictionary' ]

        try:
            html = urlopen(self.baseURL+'/'+ self.WORD)
            super().__init__(html, 'html.parser')
            self._dic_area = self.find('span', class_='dictentry')# span,  class= 'dictentry' 
            print('New Instance created !!')
        except :
          print("Connection Error")



    def get_Dic_contents(self, _wd):
        '''
        return True if Succesful
        '''
        self.WORD = _wd
        try:
            html = urlopen(self.baseURL+'/'+ _wd)
            super().__init__(html, 'html.parser')
            #print('Dic_Contents called')
        except :
          print("Connection Error")

        self.__dics = self.find('span', text=self.DICS[self._dic_num])

        if self.__dics:
            self._dic_area = self.__dics.parent # span,  class= 'dictentry' 
            return True
        else:
            #   print('Word or Dictionary is not available')
               self.WORD=''
               return False

    def _get_word_(self):
        self.word = self._dic_area.find('span', class_='HWD').text
        return self.word


    def _get_hyphen_(self, _wd):
        if self.WORD == _wd:
            self.hyphenation = self._dic_area.find('span', class_='PronCodes').text.strip()

        elif self.get_Dic_contents(_wd):
            self.hyphenation = self._dic_area.find('span', class_='PRON').text.strip()
            self.WORD = _wd
            return self.hyphenation
        else:
            return ''

    def _get_hyphen_audio(self, _wd,_n = 0):
        _nation = ['speaker amefile','speaker brefile' ]

        if self.WORD == _wd:
            _mp3_html = self._dic_area.find('span',class_ =re.compile(_nation[_n]))
            _mp3_url = 'https://www.ldoceonline.com'+_mp3_html.get('data-src-mp3')
            _mp3_save_path = '.' + '/' + self.DIC_NAME+'/'+ _mp3_html.get('data-src-mp3')

        elif self.get_Dic_contents(_wd):
            _mp3_html = self._dic_area.find('span',class_ =re.compile(_nation[_n]))
            _mp3_url = 'https://www.ldoceonline.com'+_mp3_html.get('data-src-mp3')
            _mp3_save_path = '.' + '/' + self.DIC_NAME +'/'+ _mp3_html.get('data-src-mp3')
        else:
            return 'No Mp3'


        _mp3_html = self._dic_area.find('span',class_ =re.compile(_nation[_n]))
        _mp3_url = 'https://www.ldoceonline.com'+_mp3_html.get('data-src-mp3')
        _mp3_save_path = '.' + '/' + self.DIC_NAME+'/'+ _mp3_html.get('data-src-mp3')

        if os.path.exists(os.path.dirname(_mp3_save_path)):
            pass
        else:
            os.makedirs(os.path.dirname(_mp3_save_path))
        _DN_ = ldoce_dn() 

        _DN_.save(_mp3_url, _mp3_save_path) 
        return _mp3_save_path


    def _get_def(self, _wd):
        if self.WORD == _wd:
            _DEF =  [x.text.strip() for x  in self._dic_area.find_all('span', class_='DEF')]
        elif self.get_Dic_contents(_wd):
            _DEF =  [x.text.strip() for x  in self._dic_area.find_all('span', class_='DEF')]
            return _DEF 
        else:
            return ''


    def _get_exam(self, _wd):
        if self.WORD == _wd:
            _EXAM = [ x.text[1:] if x.text.startswith('\xa0') else x.text for x in self._dic_area.find_all('span', class_='EXAMPLE')]
        else:
            self.get_Dic_contents(_wd)
            _EXAM = [ x.text[1:] if x.text.startswith('\xa0') else x.text for x in self._dic_area.find_all('span', class_='EXAMPLE')]
        return _EXAM



    def _get_exam_corpus(self, _wd):
        if self.WORD == _wd:
            _EXAM = [ x.text[1:] if x.text.startswith('\xa0') else x.text\
                      for x in self._dic_area.find_all('span', class_= re.compile('cexa1g1')) \
                      if self._dic_area.find_all('span', class_= re.compile('cexa1g1')) ]
            return _EXAM 
        elif self.get_Dic_contents(_wd):
            _EXAM = [ x.text[1:] if x.text.startswith('\xa0') else x.text\
                      for x in self._dic_area.find_all('span', class_= re.compile('cexa1g1')) \
                      if self._dic_area.find_all('span', class_= re.compile('cexa1g1')) ]
            return _EXAM
        else:
            return ''


    def _get_origin(self, _wd):

        _result = []
        if self.WORD == _wd:
            _etym = self.find_all('span', 'etym')
            for i in _etym:
                dd=i.find_all('span', class_='Sense')
                for j in dd:
                    _result.append(re.sub('\xa0','', j.text))
            return _result
    
        elif self.get_Dic_contents(_wd):
            _etym = self.find_all('span', 'etym')
            for i in _etym:
                dd=i.find_all('span', class_='Sense')
                for j in dd:
                    _result.append(j.text)

            return _result

        else:
            return ''
class Getty(BeautifulSoup):
    def __init__(self):
        self.baseURL = 'https://www.gettyimages.com/photos/'

    def get_image(self,_wd, _num=2):
        try:
            html = urlopen(self.baseURL+'/'+ _wd)
            super().__init__(html, 'html.parser')
        except :
              print("Connection Error")

        _result = self.find_all('img', class_='srp-asset-image')

        if os.path.exists(os.path.dirname('./getty_images')):
            print('No pics')
        else:
            os.makedirs(os.path.dirname('./getty_images'))
        print('=---------------')

        _lst_files =[]
        if _result:
           DN = ldoce_dn()
           i =0 
           while( i<len(_result) and i< _num):
               dn_url = _result[i].attrs['src']
               _t = time.localtime()

               directory = './getty_' + time.strftime("%y%m%d%H")
               if not os.path.exists(directory):
                   os.makedirs(directory)
               _file_path_name = directory+'/' + _wd+'-'+ str(i)+'.jpg'
               DN.save(dn_url, _file_path_name )
               _lst_files.append(_file_path_name)
               i +=1
        return _lst_files


    def merge_images(self,_lst_img, _vh='v', _show=False):
        images = map(Image.open, _lst_img)
        widths, heights = zip(*(i.size for i in images))
    
          # total_width = sum(widths)
          # max_height = max(heights)
        if _lst_img[0] == '':
            return ''
        
        if _vh.lower() =='v':
            total_height = sum(heights)
            max_width= max(widths)
            new_im = Image.new('RGB', (max_width, total_height))
            images = map(Image.open, _lst_img)
            x_offset = 0
            for im in images:
                new_im.paste(im, (0,x_offset))
                x_offset += im.size[1]


        elif _vh.lower() =='h':
            total_width = sum(widths)
            max_height= max(heights)
            new_im = Image.new('RGB', (total_width, max_height))
            images = map(Image.open, _lst_img)
            x_offset = 0
            for im in images:
                new_im.paste(im, (x_offset,0 ))
                x_offset += im.size[1]
            else:
              print('Wrong Option for Vertical, Horizontal')
        if _show :
            new_im.show()

        return new_im

    def get_merged(self, _wd, _num=2):
        _lst_files = self.get_image(_wd, _num)

        print(_lst_files)
        if not _lst_files:
            return ''

        _merged_f = self.merge_images(_lst_files)

        _fname = os.path.basename(_lst_files[0]).split('-')[0]
        _fname = _fname+'_' +time.strftime("%m%d")+'.jpg'
        _dir = os.path.dirname(_lst_files[0])+'/'
        _merged_f.save(_dir+_fname, 'JPEG')
        

        for i in _lst_files:
            try:
                os.remove(i)
            except OSError as e:
                print("Error: %s-%s"%(e.filename, e.strerror))

        return _dir+_fname

#soup = LDOCE('disclosure', 0)
# # 사전레이어 선택
# dic=soup.find('div', class_='dictionary')
# # 사전 있는지 체크
# dic.find('span', text='From Longman Dictionary of Contemporary English') 

if __name__ =="__main__":
    g_img = Getty()
    g_img.get_merged('words', 3)
