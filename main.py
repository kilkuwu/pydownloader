import os
import customtkinter as ctk
from PIL import Image, ImageTk
import yt_dlp
from winsound import MessageBeep
from threading import Thread
import tkinter.font as tkfont
import tkinter as tk
import sys
from tkinter import filedialog

class EmbedTerminal(ctk.CTkFrame):
    class StdoutRedirector(object):
        def __init__(self, textwidget):
            self.textwidget = textwidget
            
        def write(self, string):
            self.textwidget.config(state='normal')
            self.textwidget.insert('end', string)
            self.textwidget.see('end')
            self.textwidget.config(state='disabled')
        
        def flush(self):
            pass

    def __init__(self, master):
        super().__init__(master=master)

        self.font = tkfont.Font(family="Consolas", size=12)
        fg_color = ctk.CTkThemeManager.single_color(self.fg_color, self.appearance_mode)
        self.inputbox = tk.Text(
            master=self,
            font=self.font, 
            bg=fg_color,
            highlightthickness=0, 
            fg='#FFA9E0',
            selectforeground='#FFA9E0',
            insertbackground='#FFA9E0',
            borderwidth=0,
            spacing1=2,
            spacing2=2,
            spacing3=2,
            selectbackground='#97C6EB'
        )       

        sys.stdout = self.StdoutRedirector(self.inputbox)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.inputbox.grid(row=0, column=0, padx=20, pady=20, sticky='nswe')

class CustomText(ctk.CTkFrame):
    def __init__(self, master, placeholder_color, placeholder):
        super().__init__(master=master)
        self.placeholder_color = placeholder_color
        self.placeholder = placeholder
        fg_color = ctk.CTkThemeManager.single_color(self.fg_color, self.appearance_mode)
        self.inputbox = tk.Text(
            master=self,
            font=('Consolas', 14), 
            bg=fg_color,
            highlightthickness=0, 
            fg='white',
            selectforeground='white',
            insertbackground='white',
            borderwidth=0,
            spacing1=2,
            spacing2=2,
            spacing3=2,
            selectbackground='#97C6EB'
        )

        self.default_fg_color = self.inputbox['fg']
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.inputbox.grid(row=0, column=0, padx=20, pady=20, sticky='nswe')
        self.inputbox.bind('<Control-BackSpace>', self.entry_ctrl_bs)
        self.inputbox.bind("<FocusIn>", self.foc_in)
        self.inputbox.bind("<FocusOut>", self.foc_out)

        self.image = Image.open(os.path.join('assets', 'images', 'fromfile.png'))

        self.inputbox.bind("<Control-o>", self.file_open)
        scale = min(32/self.image.height, 32/self.image.width)
        self.image = self.image.resize((int(scale*self.image.width), int(scale*self.image.height)), 1)
        self.image = ImageTk.PhotoImage(self.image)
        self.filebutton = ctk.CTkButton(
            master=self,
            text=None,
            width=32,
            fg_color=fg_color,
            image=self.image,
            hover_color="#484848",
            command=self.file_open
        )
        self.filebutton.grid(row=0, column=0, sticky='ne', padx=10, pady=10)
        self.put_placeholder()
    
    def file_open(self, event=None):
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
    
    def get(self):
        text = self.inputbox.get('1.0', 'end')
        return "" if self.inputbox['fg'] == self.placeholder_color or text == '\n' else text

class BrowsePath(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master=master, height=32)
        self.result = tk.StringVar()
        fg_color = ctk.CTkThemeManager.single_color(self.fg_color, self.appearance_mode)
        self.folder_entry = tk.Entry(
            master=self, 
            font=("Consolas", 14),
            bd=0,
            fg='white',
            insertbackground='white',
            highlightthickness=0,
            textvariable=self.result,
            bg=fg_color
        )
        self.folder_entry.bind('<Return>', self.resolve_path)
        self.folder_entry.grid(row=0, column=0, padx=10, sticky='we')

        self.image = Image.open(os.path.join('assets', 'images', 'browseicon.png'))
        scale = min(self.width/self.image.height, self.height/self.image.width)
        self.image = self.image.resize((int(scale*self.image.width), int(scale*self.image.height)), 1)
        self.image = ImageTk.PhotoImage(self.image)

        self.folder_browse = ctk.CTkButton(
            master=self,
            text=None,
            width=32,
            command=self.button_directory,
            fg_color=fg_color,
            image=self.image,
            hover_color="#484848"
        )
        self.folder_browse.grid(row=0, column=1, padx=10, sticky='e')
        self.grid_columnconfigure(0, weight=1)
        self.result.set('.')
        self.resolve_path()
    
    def button_directory(self):
        filepath = filedialog.askdirectory()
        self.result.set(filepath)
        self.resolve_path()

    def resolve_path(self, event=None):
        path = self.result.get()
        abspath = os.path.abspath(path)
        self.result.set(abspath)
        self.focus()

class BaseFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master=master)
        self.init_ui()

    def init_ui(self):
        pass

    def when_change(self):
        pass

class HomeFrame(BaseFrame):
    def init_ui(self):
        # 1x2 grid configure
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, minsize=200)
        self.grid_rowconfigure(0, weight=1)

        # Two main frames
        self.left_frame = ctk.CTkFrame(master=self)
        self.left_frame.grid(row=0, column=0, sticky="nswe", padx=(10, 5), pady=10)
    
        self.right_frame = ctk.CTkFrame(master=self)
        self.right_frame.grid(row=0, column=1, sticky="nswe", padx=(5, 10), pady=10)

        # Left frame 
        self.left_frame.grid_columnconfigure(1, weight=1)
        self.left_frame.grid_rowconfigure(1, weight=1)

        # Save folder access
        self.folder_label = ctk.CTkLabel(
            master=self.left_frame,
            text='Save:',
            text_font=('Open Sans', 14, 'bold')
        )
        self.folder_label.grid(row=0, column=0, padx=(20, 0), pady=(20, 10), sticky='w')

        self.browsepath = BrowsePath(self.left_frame)
        self.browsepath.grid(row=0, column=1, padx=(0, 20), pady=(20, 10), sticky='we')

        # Url input
        self.urlinput = CustomText(self.left_frame, 'gray', 'Put your urls here.')
        self.urlinput.grid(row=1, column=0, columnspan=2, padx=20, pady=(10, 20), sticky="nswe")
        
        # Right frame
        self.right_frame.grid_rowconfigure(4, weight=1)
        self.right_frame.grid_columnconfigure(0, weight=1)

        # Program Label
        self.programlabel = ctk.CTkLabel(
            master=self.right_frame, 
            text=PyDL.PROGRAM,
            text_font=('Open Sans', 32, 'italic', 'bold')
        )
        self.programlabel.grid(row=0, column=0, pady=(10,100), padx=10, sticky='wens')

        # Option to download video
        self.video_switch = ctk.CTkSwitch(
            master=self.right_frame, 
            width=75,
            height=25,
            text='Video', 
            text_font = ('Open Sans', 12, 'bold'),
        )
        self.bind("<Alt-v>", self.video_switch.toggle)
        self.video_switch.grid(row=2, column=0, padx=20, pady=10, sticky='we')

        self.inplaylist_switch = ctk.CTkSwitch(
            master=self.right_frame, 
            width=75,
            height=25,
            text='Playlist', 
            text_font = ('Open Sans', 12, 'bold')
        )
        self.bind("<Alt-p>", self.inplaylist_switch.toggle)
        self.inplaylist_switch.grid(row=3, column=0, padx=20, pady=10, sticky='we')

        self.bind("<Shift-Return>", self.execute)
        self.download_button = ctk.CTkButton(
            master=self.right_frame,
            text='Download',
            fg_color=ctk.CTkThemeManager.single_color(self.right_frame.fg_color, self.right_frame.appearance_mode),
            hover_color='#484848',
            text_font=('Open Sans', 16, 'bold'),
            command=self.execute
        )
        self.download_button.grid(row=4, column=0, sticky='wse', padx=10, pady=20)
    
    def execute(self, _=None):
        folder = self.browsepath.result.get()
        if not folder:
            raise Exception("Save folder not provided")
        urls = [line for line in self.urlinput.get().splitlines() if line]
        if not urls:
            raise Exception("No urls or queries found")
        info = {
            'folder': folder,
            'video': self.video_switch.get(),
            'playlist': self.video_switch.get(),
            'urls': urls
        }   
        self.master.info.update(info)
        self.master.change_frame('execute')
    
class ExecutionFrame(BaseFrame):
    def __init__(self, master):
        super().__init__(master=master)

    def init_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.left_frame = ctk.CTkFrame(master=self)
        self.left_frame.grid(row=0, column=0, sticky="nswe", padx=(20, 10), pady=20)

        self.left_frame.grid_columnconfigure(0, weight=1)
        self.left_frame.grid_rowconfigure(0, weight=1)

        self.embed_terminal = EmbedTerminal(master=self.left_frame)
        self.embed_terminal.grid(row=0, column=0, padx=10, pady=10, sticky='wens')
    
        self.right_frame = ctk.CTkFrame(master=self)
        self.right_frame.grid(row=0, column=1, sticky="nswe", padx=(10, 20), pady=20)

        self.right_frame.grid_rowconfigure(1, weight=1)
        self.right_frame.grid_columnconfigure(0, weight=1)

        self.info = ctk.CTkFrame(master=self.right_frame)
        self.info.grid(row=0, column=0, sticky="nswe", padx=10, pady=(10, 5))

        self.progress_frame = ctk.CTkFrame(master=self.right_frame)
        self.progress_frame.grid(row=1, column=0, sticky="nswe", padx=10, pady=(5, 10))
        
        self.progress_frame.grid_columnconfigure(0, weight=1)
        self.progress_frame.grid_rowconfigure(1, weight=1)
        self.progress_frame.grid_rowconfigure(2, weight=1)
        self.progress_frame.grid_rowconfigure(4, weight=1)
        self.partial_progress = ctk.CTkProgressBar(
            master=self.progress_frame,
            height=16,
        )
        self.partial_progress.grid(row=1, column=0, padx=(35, 0), pady=20, sticky='we')
        self.partial_progress_percent = ctk.CTkLabel(
            master=self.progress_frame,
            text='0.00 %',
            text_font=('Open Sans', 12),
            width=25
        )
        self.partial_progress_percent.grid(row=1, column=1, padx=(0, 35), pady=20, sticky='e')

        self.total_progress = ctk.CTkProgressBar(
            master=self.progress_frame,
            height=16,
        )
        self.total_progress.grid(row=2, column=0, padx=(35, 0), pady=20, sticky='we')
        self.total_progress_percent = ctk.CTkLabel(
            master=self.progress_frame,
            text='0.00 %',
            text_font=('Open Sans', 12),
            width=25,
        )
        self.total_progress_percent.grid(row=2, column=1, padx=(0, 35), pady=20, sticky='e')
        self.bind("<Shift-Return>", self.home)
        self.finish_button = ctk.CTkButton(
            master=self.progress_frame,
            text='Finish',
            fg_color=ctk.CTkThemeManager.single_color(self.right_frame.fg_color, self.right_frame.appearance_mode),
            hover_color='#484848',
            text_font=('Open Sans', 16, 'bold'),
            command=self.home
        )
        self.finish_button.grid(row=4, column=1, sticky='se', padx=10, pady=20)
        self.finish_button.configure(state='disabled')
        self.update_idletasks()
    
    def home(self):
        self.finish_button.configure(state='disabled')
        self.master.info.clear()
        self.master.change_frame('home')
    
    def when_change(self):
        Thread(target=self.download, kwargs={'info': self.master.info}).start()
    
    def download(self, info=None):
        def progress_hook(data):
            if not 'downloaded_bytes' in data:
                ratio = 1
            else:
                ratio = data['downloaded_bytes']/data['total_bytes']
            self.partial_progress.set(ratio)
            self.partial_progress_percent.config(text=f'{ratio*100:.2f} %')

        def postprocessor_hook(data):
            pass 

        if not info:
            e = Exception('Not enough info to begin fetching')
            self.master.error_handler(None, e, None)
            
        folder = info['folder']
        video = info['video']
        playlist = info['playlist']
        urls = info['urls']

        opts = {
            "format": "bestaudio/best",
            "nocheckcertificate": True,
            "outtmpl": {
                "default": os.path.join(folder, '%(title)s.%(ext)s')
            },
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
            }],
            "default_search": "auto",
            "source_address": "0.0.0.0",
            "progress_hooks": [progress_hook],
            "postprocessor_hooks": [postprocessor_hook]
        }

        if video == 1:
            opts['format'] = "bestvideo[ext=mp4]/best"
            opts['postprocessors'] = [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }]
        
        if playlist != 1:
            opts['noplaylist'] = True

        ytdl = yt_dlp.YoutubeDL(opts)
        
        length = len(urls)
        delta = 1.0/length
        pg = 0
        for i, url in enumerate(urls):
            self.total_progress.set(pg)
            self.total_progress_percent.config(text=f"{pg*100:.2f} %")
            self.partial_progress.set(0)
            self.partial_progress_percent.config(text=f"0.00 %")
            try:
                data = ytdl.extract_info(url)
            except yt_dlp.DownloadError as e:
                try:
                    data = ytdl.extract_info(url, force_generic_extractor=True)
                except yt_dlp.DownloadError as e:
                    self.master.error_handler(None, e, None)
            pg+=delta
            
        self.partial_progress.set(1)
        self.partial_progress_percent.config(text="100.00 %")
        self.total_progress.set(1)
        self.total_progress_percent.config(text=f"100.00 %")
        self.finish_button.configure(state='normal')

class ErrorPopup(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master=master)
        self.withdraw()
        self.title('Exception occured')
        self.grid_columnconfigure(1, weight=1)
        self.attributes("-topmost", True)
        self.message = ctk.CTkButton(
            image=ImageTk.PhotoImage(Image.open(os.path.join('assets', 'images', 'erroricon.png')).resize((25, 25))), 
            master=self,
            text=None,
            text_font=('Open Sans', 12),
            command=self.hide
        )
        new_color = self.message.detect_color_of_master()
        self.message.config(fg_color=new_color, hover_color=new_color)
        self.message.grid(row=0, column=1, padx=20, pady=20)
        hover_color = '#484848' if self.appearance_mode else '#c6c6c6'
        ok_button  = ctk.CTkButton(
            master=self,
            text='OK',
            text_font=('Open Sans', 12),
            width=32,
            command=self.hide
        )
        ok_button.config(fg_color=new_color, hover_color=hover_color)
        ok_button.grid(row=1, column=1, padx=10, pady=10, sticky='se')
        self.bind("<Return>", lambda e: self.hide())
        curx = self.master.winfo_x()+self.master.winfo_width()//2
        cury = self.master.winfo_y()+self.master.winfo_height()//2
        self.geometry(f"+{curx}+{cury}")
    
    def hide(self):
        if self.job_id:
            self.job_id = self.after_cancel(self.job_id)
        self.withdraw()
    
    def show_error(self, error):
        self.deiconify()
        MessageBeep()
        self.message.configure(text=error)
        self.job_id = self.after(10000, self.withdraw)
        

class PyDL(ctk.CTk):
    WIDTH = 1280
    HEIGHT = 720
    VERSION = "1.0"
    PROGRAM = "≥ pdl"

    def __init__(self):
        super().__init__()

        # Initial settings
        ctk.set_appearance_mode('dark')
        ctk.set_default_color_theme('dark-blue')

        self.is_executing = False

        # Window setup
        self.title('')
        self.geometry(f"{self.WIDTH}x{self.HEIGHT}")
        self.iconphoto(True, ImageTk.PhotoImage(Image.open(os.path.join('assets', 'images', 'logo.png'))))
        self.protocol("WM_DELETE_WINDOW", self.on_closing) 
        self.report_callback_exception = self.error_handler

        self.update()

        # Main frame weight for full coverage
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.info = {}

        self.frames = {
            'home': HomeFrame(master=self),
            'execute': ExecutionFrame(master=self)
        }

        self.error_popup = ErrorPopup(master=self)

        self.current_frame = self.frames['home']
        self.current_frame.grid(row=0, column=0, sticky='wens')

    def change_frame(self, frame_name):
        self.current_frame.grid_forget()
        self.current_frame = self.frames[frame_name]
        self.current_frame.grid(row=0, column=0, sticky='wens')
        self.current_frame.when_change()

    def error_handler(self, exc, val, tb):
        self.error_popup.show_error(error=str(val))

    def on_closing(self):
        self.quit()
    
    def run(self):
        self.mainloop()


if __name__ == '__main__':
    pydl = PyDL()
    pydl.run()
    




        