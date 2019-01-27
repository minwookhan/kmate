from optparse import OptionParser
from allDic import Getty
import pandas as pd
import numpy as np
import re, os
import progressbar
from tqdm import tqdm, tqdm_pandas
# print('Option: ', options)
# print('Args: ', args)

usage = "Usage: %prog [options] arg"
parser = OptionParser()
parser.add_option("-f", "--file", dest="input_fname",
                    help="input file name .xlsx", metavar="FILE")
parser.add_option("-o", "--out", dest="output_fname",
                    help="output filename .xlsx", metavar="FILE")

parser.add_option("-v", "--verbose",
                   action="store_false", dest="verbose", default=False,
                   help="don't print status messages to stdout"    )
parser.add_option("-i", "--image", dest="images", default=0,\
                    help="Get images from GETTY")
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

print("Input file : ", INPUT_FILE,"\nOutput file: " , OUTPUT_FILE,"\n# of Image : ", IMAGES, "\nVerbose: ", VERBOSE)
input("Press ENTER to continue or Ctrl-C to cancel \n")
data = pd.read_excel(INPUT_FILE)
data.rename(columns= {'Date▲':'Date'}, inplace=True)
data['Title'] = data.Usage.str.extract('<(.*)\(')
data['Author'] = data.Usage.str.extract('<.*\((.*)\)>')
data['Date'] = data.Date.dt.date

data['Usage'] = data.Usage.str.replace("<.*\d{2}[\r\n]+",'' )
data.Usage = data.Usage.str.strip()
data.index = [ x - data.index[0] for x in data.index]
data['Cloze'] =data.apply(lambda x: x['Usage'].replace(x['Word'],'{{c1:'+x.Word+'}}'),1)  
#Getty에서 에서 이미지 가져오기

if IMAGES :
    getty = Getty()
    # tqdm.pandas(desc='Downloading')
    # data.Image = data.Stem.progress_apply(getty.get_merged,_num=int(IMAGES), _verbose=VERBOSE)

    n_iter = len(data) 
    data['Image'] = None

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
