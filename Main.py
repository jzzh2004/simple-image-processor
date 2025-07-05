from pywebio.input import *
from pywebio.output import *
from pywebio import start_server
from image_handle import imagehandle 
import os
from IO import inputhandle,output_handle

def handle():
    info = inputhandle()
    new_img, output_path ,mode= imagehandle(info)
    output_handle(new_img,output_path,mode)

if __name__ == '__main__':
    start_server(
        applications=handle,
        auto_open_webbrowser=True,
    )