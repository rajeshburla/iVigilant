import pandas as pd
import numpy as np
from xml.dom import minidom
import xml.etree.ElementTree as ET
import re


def replaceURL(df):
    df1 = pd.DataFrame(columns = df.columns)
    for index, row in df.iterrows():
        text = row['text']
        urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
        for url in urls:
            text = text.replace(url, '<URLURL>')
        df1.loc[index] = [text, row['HorBot'], row['gender']]
    return df1

def replaceUserMentions(df):
    df1 = pd.DataFrame(columns = df.columns)
    for index, row in df.iterrows():
        text = row['text']
        mentions = re.findall('(^|[^@\w])@(\w{1,15})', text)
        #print(mentions)
        for mention in mentions:
            text = text.replace('RT @' + mention[1] + ':',  '<UserMention>')
            text = text.replace('@' + mention[1], '<UserMention>')
        df1.loc[index] = [text, row['HorBot'], row['gender']]
    return df1

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
df.to_csv('truth-train1', sep='\t')
df = replaceURL(df)
df = replaceUserMentions(df)
df.to_csv('truth-train-new1', sep='\t')
print(df)