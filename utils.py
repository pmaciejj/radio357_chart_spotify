import os
from datetime import datetime

main_path = os.path.abspath(__file__)
main_path = os.path.dirname(main_path)
data_path = os.path.join(main_path,"data")

if not os.path.isdir(data_path):
    os.mkdir(data_path)

def log(str):
    ts = datetime.now()
    ts = datetime.strftime(ts,"%Y%m%d")
    with open(main_path + "\\log.txt","a+") as l:
        l.write(ts  + "\t" + str + "\n" )

def remove_forbidden_chars(file_name):
    forb_c = ["[","\\","/","*","?",":","<",",",">","|","]",'"']
    for c in forb_c:
        file_name = file_name.replace(c,"")
    return file_name