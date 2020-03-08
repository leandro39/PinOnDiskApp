import tkinter
import tkinter.filedialog
import os

root = tkinter.Tk()
root.withdraw()
tempdir = tkinter.filedialog.askdirectory()
print(tempdir)