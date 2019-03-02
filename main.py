import pandas as pd
import numpy as np
from xml.dom import minidom
import xml.etree.ElementTree as ET 

columns  = ['text', 'HorBot', 'gender']
df = pd.DataFrame(columns = columns)
with open('en/truth-train.txt') as f:
    lines = f.readlines()
    i = 0
    for line in lines:
        tokens = line.split(":::")
        file_name = tokens[0]
        tree = ET.parse('en/'+file_name+'.xml')
        root = tree.getroot()
        alltext1 = ''
        #documents = mydoc.getElementsByTagName('documents')
        for document in root.iter('document'):
            alltext1 = alltext1 + document.text
        arr = [alltext1, tokens[1], tokens[2].strip()]
        df.loc[i] = arr
        i = i + 1
        #alltext = alltext.append(alltext1)
df.to_csv('truth-train', sep='\t')