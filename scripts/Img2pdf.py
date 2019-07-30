""" This Python module describes an application that converts
an image (or multiple) to a PDF file. """

import os
import tkinter as tk
from tkinter import filedialog
import colorama
from fpdf import FPDF
from PIL import Image

def img2pdf(fp, out):
    file = os.path.basename(fp)
    img = None
    try:
        img = Image.open(fp)
    except OSError:
        print('\033[91m' + "Unable to open corrupted image file: {}".format(fp))
        return
    width, height = img.size

    pdf = FPDF(unit="pt", format=[width, height])
    pdf.set_auto_page_break(0)
    pdf.add_page()
    pdf.image(fp)

    out_file = out + "/" + os.path.splitext(file)[0] + ".pdf"
    pdf.output(out_file, "F")
    if not os.path.isfile(out_file):
        print('\033[93m' + "failed to save to {}".format(out_file))
        return
    print("saved " + file + " as " + os.path.splitext(file)[0] + ".pdf")

def main():
    colorama.init()
    root = tk.Tk()
    root.withdraw()

    files = filedialog.askopenfilenames(
        title="Select file(s)",
        filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.tga *.bmp")])
    out_path = filedialog.askdirectory(title="Select output folder")

    if not files:
        print('\033[91m' + "No files selected.")
        return
    if not out_path:
        print('\033[91m' + "No output folder specified.")
        return

    print("Saving PDF files to: {}..".format(out_path))
    for file in files:
        img2pdf(file, out_path)
    print("     Conversion" + '\033[92m' + " finished")

main()
