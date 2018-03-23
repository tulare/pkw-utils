# -*- encoding: utf-8 -*-

import re
import requests
import tkinter as tk
from PIL import Image, ImageTk
from io import BytesIO

class PhotoLabel(tk.Label) :

    def __init__(self, master, photo=None, **kwargs) :
        super().__init__(master, **kwargs)
        self.setPhoto(photo)
        
    def setPhoto(self, photo=None) :
        self.photo = None

        if isinstance(photo, memoryview) :
            image_buffer = Image.open(BytesIO(photo))
            self.photo = ImageTk.PhotoImage(image_buffer)

        if isinstance(photo, ImageTk.PhotoImage) :
            self.photo = photo

        if isinstance(photo, str) :
            if re.match('http.*://', photo) :
                image_bytes = requests.get(photo).content
            else :
                image_bytes = open(photo, 'rb').read()
            image_buffer = Image.open(BytesIO(image_bytes))
            self.photo = ImageTk.PhotoImage(image_buffer)

        self.config(image=self.photo)
