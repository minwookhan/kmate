from optparse import OptionParser
from allDic import Getty
import pandas as pd
import numpy as np
import re, os
from tqdm import tqdm, tqdm_pandas
# print('Option: ', options)
# print('Args: ', args)

def get_tts(_wd):
     tts_path = "./TTS_SOUND/"
     wd_fname = _wd+".mp3"
     if os.path.exists(tts_path):
         pass
     else:
         os.dirs(tts_path)
         gTTS(_wd).save(tts_path+wd_fname)
     return("[sound:"+wd_fname+"]")

usage = "Usage: %prog [options] arg"
parser = OptionParser()
parser.add_option("-f", "--file", dest="input_fname",
                  help="-i input_filename.xlsx", metavar="FILE")
parser.add_option("-o", "--out", dest="output_fname",
                  help="-o output_filename.csv", metavar="FILE")

parser.add_option("-v", "--verbose",
                  action="store_false", dest="verbose", default=False,
                  help="don't print status messages to stdout"    )
parser.add_option("-i", "--image", dest="images", default=0,\
                  help="-i number of images Get images from GETTY")
parser.add_option("-t", "--tts",
                  action='store_false', dest="tts", default=False,\
                  help="Get TTS from Google TTS")
#    parser.add_option("-y", "--yes", action = "store_true", default = False, dest='verbose')

(options, args) = parser.parse_args()
# print("Options : ", options)
# print("args : ", args)
# print(options.input_fname)
# print(options.images)
INPUT_FILE = options.input_fname
OUTPUT_FILE = options.output_fname
IMAGES = options.images
VERBOSE = options.verbose
TTS = options.tts

print("Input file : ", INPUT_FILE,"\nOutput file: " , OUTPUT_FILE,"\n# of Image : ", IMAGES, "\nVerbose: ", VERBOSE)
input("Press ENTER to continue or Ctrl-C to cancel \n")

data = pd.read_excel(INPUT_FILE)
data.rename(columns= {'Date▲':'Date'}, inplace=True)
data['Title'] = data.Usage.str.extract('<(.*)\(')
data['Author'] = data.Usage.str.extract('<.*\((.*)\)>')
data['Date'] = data.Date.dt.date
# 기존 컬럼 이름 정리하기
#############################################################################

data['Usage'] = data.Usage.str.replace("<.*\d{2}[\r\n]+",'' )
data.Usage = data.Usage.str.strip()
data.index = [ x - data.index[0] for x in data.index]
data['Cloze'] =data.apply(lambda x: x['Usage'].replace(x['Word'],'{{c1:'+x.Word+'}}'),1)  

#발음 필드 만들어 분리하기
data['Pron'] = data.Definition.str.extract('(.*<font face.*/</font>)')
data['Definition'] = data.Definition.str.replace(".*<font face=.*</font>","")
data['Definition'] = data.Definition.str.replace("(\[<font.*?\])", r'\1 <br>')
#예문시작될때 줄 바꾸기
data['Definition']=data.Definition.str.replace("004080\"\"><i>", "00408\"\"><br><i> *", regex=True)
 

data['Image'] = None
#Getty에서 에서 이미지 가져오기
if TTS:
    tqdm.pandas(desc='Donwloding TTS')
    data.Pron = data.Pron + data.Stem.progress_apply(get_tts)

if IMAGES :
    getty = Getty()
    # tqdm.pandas(desc='Downloading')
    # data.Image = data.Stem.progress_apply(getty.get_merged,_num=int(IMAGES), _verbose=VERBOSE)

    n_iter = len(data) 

    data_image = data.Image.copy()
    data_stem = data.Stem.copy()
    with tqdm(total=n_iter, position=1, bar_format='{desc}', desc='DOWNLOADING IMAGE FROM GETTY') as desc:
        for k, i in tqdm(enumerate(data_stem), total=n_iter, position=0):
            data_image[k] = getty.get_merged(i,  int(IMAGES), VERBOSE)
            desc.set_description('Word: %s --> %s' % (i, data_image[k]))
        data.Image = data_image
    data['Image'] = data.Image.apply(lambda x:  "<img src=\""+os.path.basename(x)+"\""+">")

# <img src ="파일이름"> 만들기

data.to_csv(OUTPUT_FILE, sep="\t", index=False)
print('------------------------------\n')
print(" %i words  exported to %s "% (len(data), OUTPUT_FILE))
