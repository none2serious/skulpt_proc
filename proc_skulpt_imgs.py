import argparse
import pandas as pd
import numpy as np
from datetime import datetime as dt
import os
from PIL import Image
import pytesseract
import glob
from tqdm import tqdm


def to_float(x):
    try:
        y = float(x)
    except:
        y = np.nan
    return y

def get_file_time(filename:str)->tuple:
    ts = os.path.getmtime(filename)
    o = dt.fromtimestamp(ts)
    ostr = o.strftime("%m.%d.%Y@%H:%M:%S")
    return(ts, ostr)

def get_time_str(img)->str:
    res_ht = img.height * 0.03
    res_wd = img.width * 0.18
    top = int(img.height * 0.002)
    left = int(img.width * 0.41)
    bottom = int(top + res_ht)
    right = int(left + res_wd)
    cr = img.crop((left, top, right, bottom))
    ocrtxt = pytesseract.image_to_string(cr, timeout=5).strip()
    return(ocrtxt)

def get_frontback(img)->str:
    """
    Is it a front or back image?
    """
    res_ht = img.height * 0.043
    res_wd = img.width * 0.125
    top = img.height * 0.3025
    left = int(img.width * 0.005)
    bottom = int(top + res_ht)
    right = int(left + (1.55*res_wd))
    cr = img.crop((left, top, right, bottom))
    ocrtxt = pytesseract.image_to_string(cr, timeout=5)
    if 'Back' in ocrtxt:
        ret = "back"
    elif "Shoulder" in ocrtxt:
        ret = "front"
    else:
        ret = "failed"
    return(ret)

def get_image_type(img):
    """
    Return best guess of image type.
    Bodyfat vs. MuscleQ.
    """
    # Crop image proportionally
    top = int(img.height * 0.07)
    left = int(img.width * 0.16)
    bottom = int(img.height * 0.08)
    right = int(img.width * 0.42)
    cr = img.crop((left, top, right, bottom))
    clist = cr.getcolors()
    l = [c[0] for c in clist]
    max_value = max(l)
    idx = l.index(max_value)
    mean_color = np.array(clist[idx][1]).mean()
    red_value = np.array(clist[idx][1])[0]
    if red_value > 128:
        return("bf")
    else:
        return("mq")

def get_image_values(img, side)->list:
    res_ht = img.height * 0.043
    res_wd = img.width * 0.125
    vstep = img.height * 0.063
    hstep = 55
    top    = int(img.height * 0.457)
    left   = int(img.width * 0.005)
    bottom = int(top + res_ht)
    right  = int(left + res_wd)
    hand = ["left","right"]
    labels = {}
    labels["back"] = ["upper_back","triceps","lower_back","glutes","hamstrings","calves"]
    labels["front"] = ["shoulder","chest","biceps","abs","forearm","quads"]
    
    top = int(img.height * 0.332)
    vals = {}
    for k in range(6):
        vstep = img.height * 0.0618
        res_ht = img.height * 0.043
        res_wd = img.width * 0.125
        left = int(img.width * 0.005)
        bottom = int(top + res_ht)
        right = int(left + res_wd)
        cr = img.crop((left, top, right, bottom))
        ocrtxt = pytesseract.image_to_string(cr, timeout=5)
        vals[f"left_{labels[side][k]}"] = ocrtxt.strip()
        top = top + vstep

    top = int(img.height * 0.332)
    left = left + (img.width * 0.865)
    for k in range(6):
        vstep = img.height * 0.0618
        res_ht = img.height * 0.043
        res_wd = img.width * 0.125
        bottom = int(top + res_ht)
        right = int(left + res_wd)
        cr = img.crop((left, top, right, bottom))
        ocrtxt = pytesseract.image_to_string(cr, timeout=5)
        
        vals[f"right_{labels[side][k]}"] = ocrtxt.strip()
        top = top + vstep
    return(vals)
    # return(left, top, right, bottom)

def proc_skulpt_image(imgpath:str)->dict:
    """
    Loads a screen capture from the skulpt app and
    returns measurements and metadata. 
    Args:
        imgpath:str Full path to image on disk.
    Returns:
        res:dict python dict with the following fields:
            datestr : str date of file creation(caution)
            scrtime : str time shown on screen capture image
            kind : str    bodyfat vs. muscle quality scan
            side : str    front or back of body
            imgname : str filename on disk
            tstamp : str  unix timestamp for file creation
                          (may not always reflect capture time)
            tstamp : str  unix timestamp for file creation
                          (may not always reflect capture time)
            +left & right side values for each bodypart
    """
    img = Image.open(imgpath)
    side = get_frontback(img)
    kind = get_image_type(img)
    vals = get_image_values(img, side)
    scrtime = get_time_str(img)
    imgname = os.path.split(imgpath)[-1].split('.')[0]
    ts, tstr = get_file_time(imgpath)
    res = {}
    res["datestr"] = tstr.split("@")[0]
    res["scrtime"] = scrtime
    res["kind"] = kind
    res["side"] = side
    res["imgname"] = imgname
    res["tstamp"] = ts
    res["tstr"] = tstr
    res.update(vals)
    return(res)


def cols_to_float(df:pd.DataFrame):
    lcol = [c for c in df.columns if 'left' in c]
    rcol = [c for c in df.columns if 'right' in c]
    for l in lcol:
        df[l] = df[l].apply(lambda x: to_float(x))
    for r in rcol:
        df[r] = df[r].apply(lambda x: to_float(x))


# flist = glob("/Users/stan/Data/SkulptImages/*.PNG")
def get_skulpt_values(flist:list)->list:
    datlist = []
    for fil in tqdm(flist, desc="Processing Skulpt images"):
        # print(f'{fil}', end='', flush=True)
        dat = proc_skulpt_image(fil)
        datlist.append(dat)
        
    # for fil in flist:
    #     dat = proc_skulpt_image(fil)
    #     datlist.append(dat)
    return(datlist)

def dat_to_df(datlist:list)->dict:
    front_mqdata = []
    front_bfdata = []
    back_mqdata = []
    back_bfdata = []

    for d in datlist:
        if d["kind"] == 'mq':
            if d["side"] == 'front':
                front_mqdata.append(d)
            else:
                back_mqdata.append(d)

        elif d["kind"] == "bf":
            if d["side"] == 'front':
                front_bfdata.append(d)
            else:
                back_bfdata.append(d)
        else:
            print("error")

    f_mqdf = pd.DataFrame(front_mqdata)
    b_mqdf = pd.DataFrame(back_mqdata)

    f_bfdf = pd.DataFrame(front_bfdata)
    b_bfdf = pd.DataFrame(back_bfdata)
    
    res = {}
    res["f_mqdf"] = f_mqdf
    res["b_mqdf"] = b_mqdf
    res["f_bfdf"] = f_bfdf
    res["b_bfdf"] = b_bfdf
    
    return(res)

def keepcols():
    cols = ['datestr',
            'left_triceps',
            'left_hamstrings',
            'left_calves',
            'left_quads',
            'left_biceps',
            'left_abs',
            'right_triceps',
            'right_hamstrings',
            'right_calves',
            'right_quads',
            'right_biceps',
            'right_abs']
    return(cols)

def partslist():
    pl = ['left_triceps',
         'left_hamstrings',
         'left_calves',
         'left_quads',
         'left_biceps',
         'left_abs',
         'right_triceps',
         'right_hamstrings',
         'right_calves',
         'right_quads',
         'right_biceps',
         'right_abs']
    return(pl)

def proc_skulpt_list(flist:list)->pd.DataFrame:

    datlist = get_skulpt_values(flist)
    dfdict = dat_to_df(datlist)

    for df in ["f_mqdf", "b_mqdf", "f_bfdf", "b_bfdf"]:
        cols_to_float(dfdict[df])
    
    MQ = pd.merge(dfdict["f_mqdf"], dfdict["b_mqdf"], on="datestr")
    BF = pd.merge(dfdict["f_bfdf"], dfdict["b_bfdf"], on="datestr")
    
    MQ = MQ[keepcols()]
    BF = BF[keepcols()]

    mqdict = {p:f"mq_{p}" for p in partslist()}
    bfdict = {p:f"bf_{p}" for p in partslist()}

    x = MQ.rename(columns=mqdict, errors='raise')
    y = BF.rename(columns=bfdict, errors='raise')
    z = pd.merge(x, y, on='datestr')
    dat = pd.merge(x, y, on='datestr')
    return(dat)

def nowstr():
    now = dt.now()
    date_str = now.strftime("%m_%d_%Y-%H:%M:%S")
    return(date_str)
    
def main(input_folder, dest_folder):
    print(f'Input folder: {input_folder}')
    print(f'Destination folder: {dest_folder}')
    flist = glob.glob(f"{input_folder}/*.PNG")
    res = proc_skulpt_list(flist)
    try:
        res.to_csv(f"{dest_folder}/skulpt_data_{nowstr()}.csv", index=False)
    except:
        print(f"Error writing to {dest_folder}/skulpt_data_{nowstr()}.csv")
        res.to_csv(f"{dest_folder}/skulpt_data_{nowstr()}.csv", index=False)
        print(f"Saved in current directory as:skulpt_data_{nowstr()}.csv")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some files.')
    parser.add_argument('input_folder', type=str, help='The input folder')
    parser.add_argument('dest_folder', type=str, help='The destination folder')

    args = parser.parse_args()
    main(args.input_folder, args.dest_folder)
