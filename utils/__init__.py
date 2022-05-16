import sys
import tkinter as tk
import tkinter.font as tkfont
from turtle import color
import customtkinter as ctk
from PIL import Image, ImageTk
import os 
from tkinter import filedialog
import re

def escape_ansi(line):
    ansi_escape =re.compile(r'(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]')
    return ansi_escape.sub('', line)

print(escape_ansi(line = '\t\u001b[0;35mSomeText\u001b[0m\u001b[0;36m172.18.0.2\u001b[0m'))

class VT100:
    def __init__(self, text_wig, string=None):
        self.txtwig = text_wig
        self.i = 0; self.j = 1
        if string:
            self.loadTags()
            self.parser(string)

    def loadTags(self):
        font_name = self.txtwig['font']
        bold_font = tkfont.nametofont(font_name).copy()
        bold_font.config(weight="bold")
        italic_font = tkfont.nametofont(font_name).copy()
        italic_font.config(slant="italic")
        self.txtwig.tag_config('1', font=bold_font)
        self.txtwig.tag_config('3', font=italic_font)
        self.txtwig.tag_config('4', underline=1)
        self.txtwig.tag_config('9', overstrike=1)
        self.pallet8 = [
            "black", "red", "green", "yellow", "blue", "magenta",
            "cyan", "white", "magic", "default", # magic: enable 256 color
        ]
        for i in range(8): # pallet8
            self.txtwig.tag_config(str(i+30), foreground=self.pallet8[i])
            self.txtwig.tag_config(str(i+40), background=self.pallet8[i])
        pallet16 = [
            "000000","800000","008000","808000","000080","800080","008080","c0c0c0",
            "808080","ff0000","00ff00","ffff00","0000ff","ff00ff","00ffff","ffffff",
        ]
        for i in range(16): # 0-15/256-colors
            self.txtwig.tag_config(str(i)+"fg", foreground="#"+pallet16[i])
            self.txtwig.tag_config(str(i)+"bg", background="#"+pallet16[i])
        xx = [ "00", "5f", "87", "af", "d7", "ff" ]
        for i in range(0, 216): # 16-231/256-colors
            prefix = str(i+16); rgb = "#"+xx[i//36]+xx[(i//6)%6]+xx[i%6]
            self.txtwig.tag_config(prefix+"fg", foreground=rgb)
            self.txtwig.tag_config(prefix+"bg", background=rgb)
        for i in range(24): # 232-255/256-colors
            prefix = str(i+232); rgb = "#"+hex(i*10+8)[2:]*3
            self.txtwig.tag_config(prefix+"fg", foreground=rgb)
            self.txtwig.tag_config(prefix+"bg", background=rgb)

    def tagSGR(self, code):
        if code == "": return
        if   self.ext == "485": code += "bg"; self.ext = ""
        elif self.ext == "385": code += "fg"; self.ext = ""
        elif self.ext: self.ext += code; return; # 2nd skip
        elif code in [ "38", "48" ]: self.ext = code; return;
        else: code = int(code) # escape precision ie. 01
        if code == 0: return # ignore 0
        self.txtwig.tag_add(code, self.pre, self.cur)
        return code

    def de_code(self, fp):
        self.ext = ""; fbreak = fp
        while self.string[fp] != 'm':
            if self.string[fp] == ";":
                self.tagSGR(self.string[fbreak:fp])
                fbreak = fp + 1
            fp += 1
        self.tagSGR(self.string[fbreak:fp])

    def parser(self, string):
        self.cur = ""
        fp = cflag = code = 0
        length = len(string)
        self.string = string
        while fp < length:
            if string[fp]=='\x1b':
                self.pre = self.cur
                self.cur = str(self.j) + '.' +str(self.i) #self.txtwig.index(tk.CURRENT)
                pcode = code; code = fp + 2 # +2 shift escape sequence
                while string[fp] != "m": fp += 1
                fp += 1; cflag += 1
                if cflag == 2:
                    self.de_code(pcode); cflag -= 1;
                continue
            if string[fp] == '\n': self.j += 1; self.i = -1
            self.txtwig.insert("end", string[fp])
            fp += 1; self.i += 1

class EmbedTerminal(ctk.CTkFrame):

    class StdoutRedirector(object):
        def __init__(self, textwidget):
            self.color_formatter = VT100(textwidget)
            
        def write(self, string):
            self.color_formatter.txtwig.config(state='normal')
            self.color_formatter.parser(string)
            self.color_formatter.txtwig.see('end')
            self.color_formatter.txtwig.config(state='disabled')
        
        def flush(self):
            pass

    def __init__(self, master):
        super().__init__(master=master)
        self.result = tk.StringVar()
        self.inputbox = tk.Text(
            master=self,
            font=('Consolas', 12), 
            bg=ctk.CTkThemeManager.single_color(self.fg_color, self.appearance_mode),
            highlightthickness=0, 
            fg='white',
            insertbackground='white',
            borderwidth=0,
            spacing1=2,
            spacing2=2,
            spacing3=2,
            selectbackground='#97C6EB',
        )
        self.inputbox.config(
            selectforeground=self.inputbox['fg']
        )
        self.default_fg_color = self.inputbox['fg']

        sys.stdout = self.StdoutRedirector(self.inputbox)
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.inputbox.grid(row=0, column=0, padx=20, pady=20, sticky='nswe')
        self.change_mode(self.appearance_mode)

    def change_mode(self, mode):
        fg_color=ctk.CTkThemeManager.single_color(self.fg_color, self.appearance_mode)
        if mode:
            fg = self.default_fg_color = 'white'
        else:
            fg = self.default_fg_color = 'black'
        self.inputbox.config(bg=fg_color, fg=fg, insertbackground=fg)
        self.inputbox.config(
            selectforeground=self.inputbox['fg']
        )

class CustomText(ctk.CTkFrame):
    def __init__(self, master, placeholder_color, placeholder):
        super().__init__(master=master)
        self.placeholder_color = placeholder_color
        self.placeholder = placeholder
        self.result = tk.StringVar()
        self.inputbox = tk.Text(
            master=self,
            font=('Consolas', 14), 
            bg=ctk.CTkThemeManager.single_color(self.fg_color, self.appearance_mode),
            highlightthickness=0, 
            fg='white',
            insertbackground='white',
            borderwidth=0,
            spacing1=2,
            spacing2=2,
            spacing3=2,
            selectbackground='#97C6EB',
        )
        self.inputbox.config(
            selectforeground=self.inputbox['fg']
        )
        self.default_fg_color = self.inputbox['fg']
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.inputbox.grid(row=0, column=0, padx=20, pady=20, sticky='nswe')
        self.inputbox.bind('<Control-BackSpace>', self.entry_ctrl_bs)
        self.inputbox.bind("<FocusIn>", self.foc_in)
        self.inputbox.bind("<FocusOut>", self.foc_out)

        self.imagewhite = Image.open(os.path.join('assets', 'images', 'fromfilewhite.png'))
        self.image = Image.open(os.path.join('assets', 'images', 'fromfile.png'))
        scale = min(32/self.image.height, 32/self.image.width)
        self.imagewhite = self.imagewhite.resize((int(scale*self.image.width), int(scale*self.image.height)), 1)
        self.image = self.image.resize((int(scale*self.image.width), int(scale*self.image.height)), 1)
        self.image = ImageTk.PhotoImage(self.image)
        self.imagewhite = ImageTk.PhotoImage(self.imagewhite)
        self.filebutton = ctk.CTkButton(
            master=self,
            text=None,
            width=32,
            fg_color=ctk.CTkThemeManager.single_color(self.fg_color, self.appearance_mode),
            image=self.imagewhite,
            hover_color="#484848",
            command=self.file_open
        )
        self.filebutton.grid(row=0, column=0, sticky='ne', padx=10, pady=10)
        self.put_placeholder()
    
    def change_mode(self, mode):
        fg_color=ctk.CTkThemeManager.single_color(self.fg_color, self.appearance_mode)
        if mode:
            image = self.imagewhite
            fg = self.default_fg_color = 'white'
            hover_color = '#484848'
        else:
            image = self.image
            fg = self.default_fg_color = 'black'
            hover_color = '#c6c6c6'
        if self.inputbox['fg'] == self.placeholder_color:
            fg = self.placeholder_color
        self.inputbox.config(bg=fg_color, fg=fg, insertbackground=fg)
        self.inputbox.config(
            selectforeground=self.inputbox['fg']
        )
        self.filebutton.config(hover_color=hover_color, fg_color=fg_color, image=image)
    
    def file_open(self):
        file = filedialog.askopenfile()
        if file is None:
            return
        self.foc_in()
        self.inputbox.delete('1.0', 'end')
        self.inputbox.insert('1.0', file.read())
        file.close()
        self.focus()
    
    def put_placeholder(self):
        self.inputbox.insert('1.0', self.placeholder)
        self.inputbox['fg'] = self.placeholder_color

    def foc_in(self, event=None):
        if self.inputbox['fg'] == self.placeholder_color:
            self.inputbox.delete('1.0', 'end')
            self.inputbox['fg'] = self.default_fg_color

    def foc_out(self, event=None):
        if self.inputbox.get('1.0', 'end') == '\n':
            self.put_placeholder()
    
    def entry_ctrl_bs(self, event=None):
        self.inputbox.delete("insert-1c wordstart", "insert")
    
    def get_text(self, *args):
        text = self.inputbox.get('1.0', 'end')
        return "" if self.inputbox['fg'] == self.placeholder_color or text == '\n' else text

class BrowsePath(ctk.CTkFrame):
    def __init__(self, master, placeholder_text):
        super().__init__(master=master, height=32)
        self.result = tk.StringVar()
        self.folder_entry = tk.Entry(
            master=self, 
            font=("Consolas", 14),
            bd=0,
            fg='white',
            insertbackground='white',
            highlightthickness=0,
            textvariable=self.result,
            bg=ctk.CTkThemeManager.single_color(self.fg_color, self.appearance_mode)
        )
        self.folder_entry.bind('<Return>', self.resolve_path)
        self.folder_entry.grid(row=0, column=0, padx=10, sticky='we')

        self.imagewhite = Image.open(os.path.join('assets', 'images', 'browseiconwhite.png'))
        self.image = Image.open(os.path.join('assets', 'images', 'browseicon.png'))
        scale = min(self.width/self.image.height, self.height/self.image.width)
        self.imagewhite = self.imagewhite.resize((int(scale*self.image.width), int(scale*self.image.height)), 1)
        self.image = self.image.resize((int(scale*self.image.width), int(scale*self.image.height)), 1)
        self.image = ImageTk.PhotoImage(self.image)
        self.imagewhite = ImageTk.PhotoImage(self.imagewhite)
        self.folder_browse = ctk.CTkButton(
            master=self,
            text=None,
            width=32,
            command=self.button_directory,
            fg_color=ctk.CTkThemeManager.single_color(self.fg_color, self.appearance_mode),
            image=self.imagewhite,
            hover_color="#484848"
        )
        self.folder_browse.grid(row=0, column=1, padx=10, sticky='e')
        self.grid_columnconfigure(0, weight=1)
        self.result.set('.')
        self.resolve_path()
    
    def change_mode(self, mode):
        fg_color=ctk.CTkThemeManager.single_color(self.fg_color, self.appearance_mode)
        if mode:
            image = self.imagewhite
            fg = 'white'
            hover_color = '#484848'
        else:
            image = self.image
            fg = 'black'
            hover_color = '#c6c6c6'
        self.folder_browse.config(fg_color=fg_color, hover_color=hover_color, image=image)
        self.folder_entry.config(bg=fg_color, fg=fg, insertbackground=fg)

    def button_directory(self):
        filepath = filedialog.askdirectory()
        self.result.set(filepath)
        self.resolve_path()

    def resolve_path(self, *args):
        path = self.result.get()
        abspath = os.path.abspath(path)
        self.result.set(abspath)
        self.focus()