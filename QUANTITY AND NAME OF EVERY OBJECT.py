# -*- coding: utf-8 -*-
"""
Created on Tue Mar 21 23:54:11 2023

@author: hless
"""


import tkinter as tk
from tkinter import filedialog
import ezdxf
import math
import pandas as pd
import sys

def browse_file():
    file_path = filedialog.askopenfilename()
    file_path_entry.delete(0, tk.END)
    file_path_entry.insert(0, file_path)
    print(file_path)
    return file_path

def read_file(file_path):
 try:
    doc = ezdxf.readfile(file_path)
 except IOError:
    status_label.config(text="Not a DXF file or a generic I/O error.")
    sys.exit(1)
 except ezdxf.DXFStructureError:
    status_label.config(text="Invalid or corrupted DXF file.")
    sys.exit(2)
    return doc


def extract_dxf_info(file_path):
    doc = ezdxf.readfile(file_path)
    msp = doc.modelspace()
    insert_info = {}
    data = []

    def layer_key(entity):
        if entity.dxf.layer == "0":  # exclude entities from default layer "0"
            return None
        else:
            return entity.dxf.layer

    group = msp.groupby(key=layer_key)
    for key, entities in group.items():
        count = len(list(entities))
        data.append({'Name': key, 'Count': count, 'Type': 'Entity'})

    for entity in msp:
        if entity.dxftype() == "INSERT":
            block_name = entity.dxf.name

            try:
                scale_factor = entity.dxf.xscale
            except AttributeError:
                scale_factor = 0

            count = int(math.ceil(abs(scale_factor)))

            if block_name not in insert_info:
                insert_info[block_name] = count
            else:
                insert_info[block_name] += count

    for block_name, count in insert_info.items():
        data.append({'Name': block_name, 'Count': count, 'Type': 'Block'})

    df = pd.DataFrame(data)

    return df



def on_extract_clicked():
    file_path = file_path_entry.get()

    try:
        global PED
        PED = extract_dxf_info(file_path)
        info_extracted_label.config(text="Information extracted")
        print(PED)
    except Exception as e:
        info_extracted_label.config(text="Error: " + str(e))


def save_to_csv():
    try:
        global PED
        if not PED.empty:
            save_path = filedialog.asksaveasfilename(defaultextension=".csv")
            if not save_path:
                return
            PED.to_csv(save_path, index=False)
            info_extracted_label.config(text="Data saved to: " + save_path)
        else:
            info_extracted_label.config(text="No data to save.")
    except Exception as e:
        info_extracted_label.config(text=str(e))


root = tk.Tk()
root.geometry("500x500")

status_label = tk.Label(root, text="Status:")
status_label.pack()

file_path_label = tk.Label(root, text="File path:")
file_path_label.pack()

file_path_entry = tk.Entry(root)
file_path_entry.pack()

browse_button = tk.Button(root, text="Browse", command=browse_file)
browse_button.pack()


extract_button = tk.Button(root, text="Extract", command=on_extract_clicked)
extract_button.pack()

save_button = tk.Button(root, text="Save", command=save_to_csv)
save_button.pack()

info_extracted_label = tk.Label(root, text="")
info_extracted_label.pack()

quit_button = tk.Button(root, text="Quit", command=root.quit)
quit_button.pack()


root.mainloop()