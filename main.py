import json
import os
import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk
import yt_dlp
from winsound import MessageBeep
from threading import Thread
from utils import CustomText, BrowsePath, EmbedTerminal

class PyDL(ctk.CTk):
    WIDTH = 1280
    HEIGHT = 720
    VERSION = "1.0"
    PROGRAM = ">PDL<"

    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode('dark')
        ctk.set_default_color_theme('dark-blue')
        self.home()
        self.report_callback_exception = self.error_handler
        self.title(self.PROGRAM)
        self.geometry(f"{self.WIDTH}x{self.HEIGHT}")
        self.icon_image = ImageTk.PhotoImage(Image.open(os.path.join('assets', 'images', 'logo.png')))
        self.iconphoto(True, self.icon_image)
        self.iconbitmap()
        self.protocol("WM_DELETE_WINDOW", self.on_closing) 
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
    
    def home(self):
        self.main_frame = ctk.CTkFrame(
            master = self
        )
        self.main_frame.tkraise()
        # configure grid layout (2x1)

        self.main_frame.grid_columnconfigure(0, minsize=10)
        self.main_frame.grid_columnconfigure(1, weight=2)
        self.main_frame.grid_columnconfigure(2, minsize=200)
        self.main_frame.grid_columnconfigure(3, minsize=10)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid(row=0, column=0, sticky='wens')

        self.left_frame = ctk.CTkFrame(master=self.main_frame)
        self.left_frame.grid(row=0, column=1, sticky="nswe", padx=10, pady=20)
    
        self.right_frame = ctk.CTkFrame(master=self.main_frame)
        self.right_frame.grid(row=0, column=2, sticky="nswe", padx=10, pady=20)

        self.left_frame.grid_columnconfigure(0, minsize=10)
        self.left_frame.grid_columnconfigure(2, weight=1)
        self.left_frame.grid_columnconfigure(4, minsize=10)

        self.folder_label = ctk.CTkLabel(
            master=self.left_frame,
            text='Save Folder:',
            text_font=('Consolas', 14, 'bold')
        )
        self.folder_label.grid(row=1, column=1, pady=10, padx=(10, 0), sticky='w')

        self.browsepath = BrowsePath(self.left_frame, 'Put your save folder here.')
        self.browsepath.grid(row=1, column=2, padx=(0, 10), pady=10, sticky='we')

        self.urlinput = CustomText(self.left_frame, 'gray', 'Put your urls here.')
        self.urlinput.grid(row=2, column=1, columnspan=3, padx=10, pady=10, sticky="nswe")
        
        self.left_frame.grid_rowconfigure(0, minsize=10)
        self.left_frame.grid_rowconfigure(2, weight=1)
        self.left_frame.grid_rowconfigure(3, minsize=10)

        self.programlabel = ctk.CTkLabel(
            master=self.right_frame, 
            text=PyDL.PROGRAM,
            text_font=('Open Sans', 32, 'italic', 'bold')
        )
        self.programlabel.grid(row=0, column=0, pady=(10,100), padx=10, sticky='wens')

        self.lightmode = ctk.CTkSwitch(
            master=self.right_frame, 
            width=50,
            height=25,
            text='Light Mode', 
            text_font = ('Open Sans', 12),
            command=self.change_mode
        )

        if not self.appearance_mode:
            self.lightmode.check_state = True 
            self.lightmode.draw(color_updates=False)

        self.bind("<Control-i>", self.lightmode.toggle)
        self.lightmode.grid(row=1, column=0, padx=20, pady=10, sticky='w')
            
        self.video_switch = ctk.CTkSwitch(
            master=self.right_frame, 
            width=50,
            height=25,
            text='As Video', 
            text_font = ('Open Sans', 12),
        )
        self.bind("<Control-o>", self.video_switch.toggle)
        self.video_switch.grid(row=2, column=0, padx=20, pady=10, sticky='w')

        self.inplaylist_switch = ctk.CTkSwitch(
            master=self.right_frame, 
            width=50,
            height=25,
            text='Playlist', 
            text_font = ('Open Sans', 12)
        )
        self.bind("<Control-p>", self.inplaylist_switch.toggle)
        self.inplaylist_switch.grid(row=3, column=0, padx=20, pady=10, sticky='w')

        self.download_button = ctk.CTkButton(
            master=self.right_frame,
            text='Download',
            fg_color=ctk.CTkThemeManager.single_color(self.right_frame.fg_color, self.right_frame.appearance_mode),
            hover_color='#484848',
            text_font=('Consolas', 16, 'bold', 'italic'),
            command=self.execute
        )
        self.download_button.grid(row=4, column=0, sticky='wse', padx=10, pady=20)
        self.right_frame.grid_rowconfigure(4, weight=1)

    def error_handler(self, exc, val, tb):
        MessageBeep()
        popup = ctk.CTkToplevel(master=self)
        popup.title('Exception occured')
        popup.grid_columnconfigure(1, weight=1)
        popup.attributes("-topmost", True)
        image = Image.open(os.path.join('assets', 'images', 'erroricon.png')).resize((25, 25))
        image = ImageTk.PhotoImage(image)
        message = ctk.CTkButton(
            image=image, 
            master=popup,
            text=str(val),
            text_font=('Open Sans', 12),
            command=popup.destroy
        )
        new_color = message.detect_color_of_master()
        message.config(fg_color=new_color, hover_color=new_color)
        message.grid(row=0, column=1, padx=20, pady=20)
        hover_color = '#484848' if popup.appearance_mode else '#c6c6c6'
        ok_button  = ctk.CTkButton(
            master=popup,
            text='OK',
            text_font=('Open Sans', 12),
            width=32,
            command=popup.destroy
        )
        ok_button.config(fg_color=new_color, hover_color=hover_color)
        ok_button.grid(row=1, column=1, padx=10, pady=10, sticky='se')
        popup.bind("<Return>", lambda e: popup.destroy())
        curx, cury = self.winfo_x()+self.WIDTH//2, self.winfo_y()+self.HEIGHT//2
        popup.geometry(f"+{curx}+{cury}")

    def change_mode(self, mode=None):
        if not mode: 
            if self.appearance_mode == 1:
                mode = 0
            else:
                mode = 1
        if mode == 0:
            hover_color = '#c6c6c6'
            ctk.set_appearance_mode('light')
            self.browsepath.change_mode(0)
            self.urlinput.change_mode(0)
        else:
            hover_color = '#484848'
            ctk.set_appearance_mode('dark')
            self.browsepath.change_mode(1)
            self.urlinput.change_mode(1)
        fg_color=ctk.CTkThemeManager.single_color(self.right_frame.fg_color, self.right_frame.appearance_mode)
        self.download_button.config(fg_color=fg_color, hover_color=hover_color)

    def on_closing(self):
        self.quit()
    
    def run(self):
        self.mainloop()

    def clear_widgets(self):
        for widget in self.winfo_children():
            widget.destroy()
    
    def execute(self):
        folder = self.browsepath.result.get()
        if not folder:
            raise Exception("Save folder not provided")
        video = self.video_switch.get()
        playlist = self.inplaylist_switch.get()
        urls = [line for line in self.urlinput.get_text().splitlines() if line]
        if not urls:
            raise Exception("No urls or queries found")

        self.clear_widgets()
        self.withdraw()
        self.deiconify()

        self.main_frame = ctk.CTkFrame(
            master = self
        )


        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid(row=0, column=0, sticky='wens')
        self.main_frame.tkraise()

        self.left_frame = ctk.CTkFrame(master=self.main_frame)
        self.left_frame.grid(row=0, column=0, sticky="nswe", padx=(20, 10), pady=20)

        self.left_frame.grid_columnconfigure(0, weight=1)
        self.left_frame.grid_rowconfigure(0, weight=1)

        self.embed_terminal = EmbedTerminal(master=self.left_frame)
        self.embed_terminal.grid(row=0, column=0, padx=10, pady=10, sticky='wens')
    
        self.right_frame = ctk.CTkFrame(master=self.main_frame)
        self.right_frame.grid(row=0, column=1, sticky="nswe", padx=(10, 20), pady=20)

        self.right_frame.grid_rowconfigure(1, weight=1)
        self.right_frame.grid_columnconfigure(0, weight=1)

        self.info = ctk.CTkFrame(master=self.right_frame)
        self.info.grid(row=0, column=0, sticky="nswe", padx=10, pady=(10, 5))

        self.progress_frame = ctk.CTkFrame(master=self.right_frame)
        self.progress_frame.grid(row=1, column=0, sticky="nswe", padx=10, pady=(5, 10))
        
        self.progress_frame.grid_columnconfigure(1, weight=1)
        self.partial_progress_percent = ctk.CTkLabel(
            master=self.progress_frame,
            text='0.00 %',
            text_font=('Open Sans', 16)
        )
        self.partial_progress_percent.grid(row=1, column=0, padx=(10, 0), pady=20, sticky='w')
        self.partial_progress = ctk.CTkProgressBar(
            master=self.progress_frame,
            height=16
        )
        self.partial_progress.grid(row=1, column=1, padx=(5, 50), pady=20, sticky='we')

        self.total_progress_percent = ctk.CTkLabel(
            master=self.progress_frame,
            text='0.00 %',
            text_font=('Open Sans', 16)
        )
        self.total_progress_percent.grid(row=2, column=0, padx=(10, 0), pady=20, sticky='w')
        self.total_progress = ctk.CTkProgressBar(
            master=self.progress_frame,
            height=16
        )
        self.total_progress.grid(row=2, column=1, padx=(5, 50), pady=20, sticky='we')
        self.update_idletasks()
        download = Thread(target=self.download_start, args=(folder, video, urls, playlist))
        download.start()

    
    def download_start(self, folder, video, urls, playlist):
        def progress_hook(data):
            ratio = data['downloaded_bytes']/data['total_bytes']
            self.partial_progress.set(ratio)
            self.partial_progress_percent.config(text=f'{ratio*100:.2f} %')
        f = open('test2.json', 'w')
        def postprocessor_hook(data):
            f.write('\n\n')
            f.write(json.dumps(data, indent=4))

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
            except yt_dlp.DownloadError:
                try:
                    data = ytdl.extract_info(url, force_generic_extractor=True)
                except yt_dlp.DownloadError as e:
                    pass
                    # self.error_handler(None, e, None)
            pg+=delta
        self.total_progress.set(1)
        self.total_progress_percent.config(text=f"100.00 %")
        f.close()


    def return_home(self):
        self.clear_widgets()
        self.withdraw()
        self.deiconify()
        self.home()



if __name__ == '__main__':
    pydl = PyDL()
    pydl.run()
    




        