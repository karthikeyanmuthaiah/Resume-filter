from tkinter import *
from pandastable import Table
from pandastable import Table, TableModel
import tkinter
from tkinter import *
import tkinter as tk
import random
import time
import os
import shutil
import pdfminer
from pdfminer.high_level import extract_text
import os
import nltk
import numpy as np
from os import listdir
from os.path import isfile, join
from io import StringIO
import pandas as pd
from collections import Counter
import en_core_web_sm
nlp = en_core_web_sm.load()

from pyresparser import ResumeParser

from spacy.matcher import PhraseMatcher
from os import path
import csv
absolutepath=path.abspath(path.curdir)
print(absolutepath)
import nltk
#nltk.download('stopwords')

from tkinter import filedialog
dirname ="global"
number_filesinbrowse ="global"

root = Tk()
root.geometry("900x600+0+0")
root.title("Resume Filtration")


#Tops = Frame(root,bg="white",width = 1600,height=50,relief=SUNKEN)
#Tops.grid(row=0)

#f1 = Frame(root,width = 50,height=50,relief=SUNKEN)
#f1.grid(row=1, sticky=E)

#f2 = Frame(root ,width = 400,height=700,relief=SUNKEN)
#f2.grid(row=2,sticky=E)

#f3 = Frame(root ,width = 400,height=400,relief=SUNKEN)
#f3.grid(row=3,sticky=E)


Tops = Frame(root,bg="white",width = 1600,height=510,relief=SUNKEN)
Tops.pack(side=TOP)

Top = Frame(root,width = 100,height=20,relief=SUNKEN)
Top.pack(side=BOTTOM,fill='both',expand=True)

f1 = Frame(root,width = 900,height=200,relief=SUNKEN)
f1.pack(side=LEFT)


#------------------TIME--------------
localtime=time.asctime(time.localtime(time.time()))
#-----------------INFO TOP------------
lblinfo = Label(Tops, font=( 'aria' ,30, 'bold' ),text="Resume Filtration",fg="steel blue",bd=10,anchor='w')
lblinfo.grid(row=0,column=0)
lblinfo = Label(Tops, font=( 'aria' ,20, ),text=localtime,fg="steel blue",anchor=W)
lblinfo.grid(row=1,column=0)
#------------------------------------------------------------------------------------
def choosefolder():
    global dirname
    dirname = filedialog.askdirectory(parent=root,initialdir="/",title='Please select a folder')
    print(dirname)
    return(dirname)
    print(dirname)
    
pt = Table(Top)
#pt.redraw()


def onlyfiles():
    print(dirname)
    mypath=(dirname)
    mypath=choosefolder() #enter your path here where you saved the resumes
    onlyfiles = [os.path.join(mypath, f) for f in os.listdir(mypath) if os.path.isfile(os.path.join(mypath, f))]
    return onlyfiles


def run():
    print(dirname)
    mypath=(dirname)
    onlyfiles = [os.path.join(mypath, f) for f in os.listdir(mypath) if os.path.isfile(os.path.join(mypath, f))]

    def pdfextract(file):
        text = extract_text(file)
        return text
    
    #function that does phrase matching and builds a candidate profile
    def create_profile(file):
        text = pdfextract(file) 
        text = str(text)
        text = text.replace("\\n", "")
        text = text.lower()
        #below is the csv where we have all the keywords, you can customize your own
        keyword_dict = pd.read_csv('https://raw.githubusercontent.com/darvinloganathan/resume-pharse/main/template.csv',error_bad_lines=False)
        stats_words = [nlp(text) for text in keyword_dict['Statistics'].dropna(axis = 0)]
        NLP_words = [nlp(text) for text in keyword_dict['NLP'].dropna(axis = 0)]
        ML_words = [nlp(text) for text in keyword_dict['Machine Learning'].dropna(axis = 0)]
        DL_words = [nlp(text) for text in keyword_dict['Deep Learning'].dropna(axis = 0)]
        R_words = [nlp(text) for text in keyword_dict['R Language'].dropna(axis = 0)]
        python_words = [nlp(text) for text in keyword_dict['Python Language'].dropna(axis = 0)]
        Data_Engineering_words = [nlp(text) for text in keyword_dict['Data Engineering'].dropna(axis = 0)]
        
        matcher = PhraseMatcher(nlp.vocab)
        matcher.add('Statstics', None, *stats_words)
        matcher.add('NLP', None, *NLP_words)
        matcher.add('MachineLearnig', None, *ML_words)
        matcher.add('DeepLearning', None, *DL_words)
        matcher.add('R', None, *R_words)
        matcher.add('Python', None, *python_words)
        matcher.add('DataEngineering', None, *Data_Engineering_words)
        
        doc = nlp(text)
        
        d = []  
        matches = matcher(doc)
        for match_id, start, end in matches:
            rule_id = nlp.vocab.strings[match_id]  # get the unicode ID, i.e. 'COLOR'
            span = doc[start : end]  # get the matched slice of the doc
            d.append((rule_id, span.text))      
        keywords = "\n".join(f'{i[0]} {i[1]} ({j})' for i,j in Counter(d).items())
        
        ## convertimg string of keywords to dataframe
        df = pd.read_csv(StringIO(keywords),names = ['Keywords_List'])
        df1 = pd.DataFrame(df.Keywords_List.str.split(' ',1).tolist(),columns = ['Subject','Keyword'])
        df2 = pd.DataFrame(df1.Keyword.str.split('(',1).tolist(),columns = ['Keyword', 'Count'])
        df3 = pd.concat([df1['Subject'],df2['Keyword'], df2['Count']], axis =1) 
        df3['Count'] = df3['Count'].apply(lambda x: x.rstrip(")"))
        
        base = os.path.basename(file)
        filename = os.path.splitext(base)[0]
           
        name = filename.split('_')
        name2 = name[0]
        name2 = name2.lower()
        ## converting str to dataframe
        name3 = pd.read_csv(StringIO(name2),names = ['Candidate Name'])
        
        dataf = pd.concat([name3['Candidate Name'], df3['Subject'], df3['Keyword'], df3['Count']], axis = 1)
        dataf['Candidate Name'].fillna(dataf['Candidate Name'].iloc[0], inplace = True)
         
        return(dataf)
        
    #function ends
            
    #code to execute/call the above functions
    
    final_database=pd.DataFrame()
    i = 0 
    while i < len(onlyfiles):
        file = onlyfiles[i]
        dat = create_profile(file)
        final_database = final_database.append(dat)
        i +=1
        print(final_database)
    
    
    #code to count words under each category and visulaize it through Matplotlib
    
    final_database2 = final_database['Keyword'].groupby([final_database['Candidate Name'], final_database['Subject']]).count().unstack()
    final_database2.reset_index(inplace = True)
    final_database2.fillna(0,inplace=True)
    new_data = final_database2.iloc[:,1:]
    new_data.index = final_database2['Candidate Name']
    new_data['Score']=new_data.sum(axis = 1, skipna = True)
    result=new_data
    result.reset_index(level=0, inplace=True)
#    base=list(result['Candidate Name'])
#    result['resume'] = np.array(base)
    total_exp=[]
    mail_id=[]
    mob_num=[]
    for i in onlyfiles:
        data = ResumeParser(i).get_extracted_data()
        a=data['total_experience']
        b=data['email']
        c=data['mobile_number']
        total_exp.append(a)
        mail_id.append(b)
        mob_num.append(c)
    te=[]
    for i in total_exp:
        if i>0:
            te.append(i)
        else:
            te.append('fresher')
    result.loc[:,'total_experience'] = pd.Series(te)
    result.loc[:,'email'] = pd.Series(mail_id)
    result.loc[:,'mobile_number'] = pd.Series(mob_num)
    result1=result.sort_values(by='Score',ascending=False)
    df = TableModel.getSampleData()
    table = pt = Table(Top, dataframe=result1,
                                   showtoolbar=True, showstatusbar=True)
    pt.show()
    
    #execute the below line if you want to see the candidate profile in a csv format
    #sample2=result.to_csv('sample.csv')
 


#-----------------------------------------buttons------------------------------------------
lblTotal = Label(f1,text="---------------------",fg="white")
lblTotal.grid(row=6,columnspan=3)

btnTotal=Button(f1,padx=16,pady=8, bd=10 ,fg="black",font=('ariel' ,16,'bold'),width=10, text="Choose Folder", bg="powder blue",command=choosefolder)
btnTotal.grid(row=0, column=0)

btnTotal=Button(f1,padx=16,pady=8, bd=10 ,fg="black",font=('ariel' ,16,'bold'),width=10, text="Output", bg="powder blue",command=run)
btnTotal.grid(row=0, column=2)

root.mainloop()