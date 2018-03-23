# -*- encoding: utf-8 -*-

import tkinter as tk
from .widgets import PhotoLabel

class BaseDialog(tk.Tk) :

    def __init__(self, **kwargs) :
        super().__init__(**kwargs)

        self.result = None

        body = tk.Frame(self)
        self.initial_focus = self.body(body)
        body.pack(padx=5, pady=5)

        self.buttonbox()

        self.grab_set()

        if not self.initial_focus :
            self.initial_focus = self

        self.protocol('WM_DELETE_WINDOW', self.cancel)
        self.initial_focus.focus_set()
        self.wait_window(self)

    def body(self, master) :
        pass # override

    def buttonbox(self):
        # add standard button box. override if you don't want the
        # standard buttons

        box = tk.Frame(self)

        w = tk.Button(
            box, text="OK", width=10, command=self.ok, default=tk.ACTIVE
        )
        w.pack(side=tk.LEFT, padx=5, pady=5)

        w = tk.Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side=tk.LEFT, padx=5, pady=5)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        box.pack()

    def ok(self, event=None) :
        if not self.validate() :
            self.initial_focus.focus_set()
            return

        self.withdraw()
        self.update_idletasks()

        self.apply()
        self.cancel()

    def cancel(self, event=None) :
        self.destroy()

    def apply(self) :
        pass #override

    def validate(self) :
        return True #override


class CaptchaLoginDialog(BaseDialog):

    def __init__(self, captcha, **kwargs) :
        self.captcha = captcha
        super().__init__(**kwargs)

    def body(self, master):
        tk.Label(master, text="User:").grid(row=0)
        tk.Label(master, text="Password:").grid(row=1)
        PhotoLabel(master, photo=self.captcha).grid(row=2, columnspan=2)
        tk.Label(master, text="Captcha:").grid(row=3)
        
        self.e1 = tk.Entry(master)
        self.e2 = tk.Entry(master)
        self.e3 = tk.Entry(master)

        self.e1.grid(row=0, column=1)
        self.e2.grid(row=1, column=1)
        self.e3.grid(row=3, column=1)

        return self.e1 # initial focus

    def apply(self):
        self.result = {
            'user' : self.e1.get(),
            'password' : self.e2.get(),
            'captcha' : self.e3.get().upper()
        }


