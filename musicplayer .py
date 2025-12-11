import tkinter as tk
from tkinter import filedialog, ttk
import pygame
import os
import time

class CompactSpatialPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Spatial Remote")
        # سایز اولیه کوچک (حالت مینی)
        self.root.geometry("350x250")
        self.root.configure(bg="#1E1E1E")
        self.root.resizable(False, False)

        # --- Audio Engine ---
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)
        
        self.channel = None 
        self.current_sound = None
        
        self.playlist_data = [] 
        self.current_index = -1
        self.is_paused = False
        self.is_playing = False
        
        self.start_time = 0
        self.pause_start_time = 0
        self.total_pause_duration = 0
        self.track_duration = 0

        # Settings
        self.var_pan = tk.BooleanVar(value=True)
        self.var_vert = tk.BooleanVar(value=True)
        self.var_min_fx = tk.BooleanVar(value=True)
        self.var_mouse = tk.BooleanVar(value=False)
        
        # New Setting: Show Cover Art (Default: False for compactness)
        self.var_show_cover = tk.BooleanVar(value=False)

        self.view_mode = "player" # 'player' or 'list'

        # Key Bindings
        self.root.bind('<space>', lambda e: self.toggle_play_pause())
        self.root.bind('<Right>', lambda e: self.next_track())
        self.root.bind('<Left>', lambda e: self.prev_track())

        # --- UI Construction ---
        self.setup_ui()
        self.process_audio_logic()

    def setup_ui(self):
        # 1. Header (Compact)
        header = tk.Frame(self.root, bg="#252525", height=40)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Button(header, text="⚙", command=self.open_settings, bg="#252525", fg="#AAA", font=("Arial", 12), relief="flat").pack(side=tk.RIGHT, padx=5)
        self.btn_view = tk.Button(header, text="☰ LIST", command=self.toggle_view, bg="#252525", fg="#00E5FF", font=("Segoe UI", 9, "bold"), relief="flat")
        self.btn_view.pack(side=tk.LEFT, padx=5)
        
        # Title/Status in Header
        self.lbl_header_title = tk.Label(header, text="Spatial Remote", bg="#252525", fg="white", font=("Segoe UI", 9))
        self.lbl_header_title.pack(side=tk.LEFT, padx=10)

        # 2. Main Content
        self.main_container = tk.Frame(self.root, bg="#1E1E1E")
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # --- PLAYER VIEW ---
        self.frame_player = tk.Frame(self.main_container, bg="#1E1E1E")
        
        # Cover Art Section (Hidden by default)
        self.frame_cover_art = tk.Frame(self.frame_player, bg="#1E1E1E")
        self.lbl_cover = tk.Label(self.frame_cover_art, text="🎵", font=("Arial", 60), bg="#1E1E1E", fg="#333")
        self.lbl_cover.pack(pady=10)
        # Note: frame_cover_art is NOT packed initially based on var_show_cover

        # Track Info (Large Text)
        self.lbl_track = tk.Label(self.frame_player, text="No Track", font=("Segoe UI", 12, "bold"), bg="#1E1E1E", fg="white", wraplength=330)
        self.lbl_track.pack(pady=(10, 5))
        
        # Big Add Button (Visible when empty)
        self.btn_add = tk.Button(self.frame_player, text="📂 OPEN FILES", command=self.add_files, bg="#6200EA", fg="white", font=("Arial", 10, "bold"), relief="flat", pady=5)
        self.btn_add.pack(pady=10)

        # Controls
        ctrl_frame = tk.Frame(self.frame_player, bg="#1E1E1E")
        ctrl_frame.pack(pady=10)
        b_sty = {"bg": "#1E1E1E", "fg": "white", "font": ("Arial", 18), "relief": "flat", "activebackground": "#333"}
        
        tk.Button(ctrl_frame, text="⏮", command=self.prev_track, **b_sty).pack(side=tk.LEFT, padx=10)
        self.btn_play = tk.Button(ctrl_frame, text="▶", command=self.toggle_play_pause, **b_sty)
        self.btn_play.pack(side=tk.LEFT, padx=10)
        tk.Button(ctrl_frame, text="⏭", command=self.next_track, **b_sty).pack(side=tk.LEFT, padx=10)

        # Progress & Time
        self.seek_var = tk.DoubleVar()
        style = ttk.Style()
        style.theme_use('default')
        style.configure("TScale", background="#1E1E1E", troughcolor="#333", sliderlength=10)
        self.p_bar = ttk.Scale(self.frame_player, from_=0, to=100, variable=self.seek_var, style="TScale")
        self.p_bar.pack(fill=tk.X, pady=(10, 0))
        
        self.lbl_time = tk.Label(self.frame_player, text="00:00 / 00:00", bg="#1E1E1E", fg="gray", font=("Arial", 8))
        self.lbl_time.pack()

        self.frame_player.pack(fill=tk.BOTH, expand=True)

        # --- LIST VIEW ---
        self.frame_list = tk.Frame(self.main_container, bg="#1E1E1E")
        self.listbox = tk.Listbox(self.frame_list, bg="#252525", fg="white", selectbackground="#00E5FF", selectforeground="black", activestyle='none', borderwidth=0, font=("Segoe UI", 10))
        self.scrollbar = tk.Scrollbar(self.frame_list, orient="vertical", command=self.listbox.yview)
        self.listbox.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.listbox.bind('<Double-1>', self.on_list_click)

    # --- Logic ---
    def update_layout(self):
        # این تابع بر اساس تنظیمات، سایز پنجره و بودن/نبودن کاور را مدیریت میکند
        if self.var_show_cover.get():
            self.frame_cover_art.pack(before=self.lbl_track, pady=10)
            self.root.geometry("350x450") # بزرگتر
        else:
            self.frame_cover_art.pack_forget()
            self.root.geometry("350x250") # کوچکتر (Compact)

    def toggle_view(self):
        if self.view_mode == "player":
            self.frame_player.pack_forget()
            self.frame_list.pack(fill=tk.BOTH, expand=True)
            self.btn_view.config(text="PLAYER")
            self.view_mode = "list"
            # در حالت لیست همیشه کمی بلندتر باشد بهتر است
            self.root.geometry("350x400")
        else:
            self.frame_list.pack_forget()
            self.frame_player.pack(fill=tk.BOTH, expand=True)
            self.btn_view.config(text="☰ LIST")
            self.view_mode = "player"
            # برگشت به سایز تنظیم شده
            self.update_layout()

    def open_settings(self):
        win = tk.Toplevel(self.root)
        win.title("Settings")
        win.geometry("260x280")
        win.configure(bg="#252525")
        tk.Label(win, text="Configuration", bg="#252525", fg="#00E5FF", font=("Arial", 10, "bold")).pack(pady=10)
        
        c_cfg = {"bg": "#252525", "fg": "white", "selectcolor": "#444", "activebackground": "#252525", "anchor": "w"}
        
        # Audio FX
        tk.Label(win, text="Audio FX:", bg="#252525", fg="gray", font=("Arial", 8)).pack(anchor='w', padx=20)
        tk.Checkbutton(win, text="Horizontal Pan (L/R)", variable=self.var_pan, **c_cfg).pack(fill=tk.X, padx=20)
        tk.Checkbutton(win, text="Vertical Vol (Up/Down)", variable=self.var_vert, **c_cfg).pack(fill=tk.X, padx=20)
        tk.Checkbutton(win, text="Min Muffle", variable=self.var_min_fx, **c_cfg).pack(fill=tk.X, padx=20)
        tk.Checkbutton(win, text="Mouse Tracking", variable=self.var_mouse, **c_cfg).pack(fill=tk.X, padx=20)
        
        # Visual
        tk.Frame(win, height=1, bg="gray").pack(fill=tk.X, padx=10, pady=5)
        tk.Label(win, text="Visual:", bg="#252525", fg="gray", font=("Arial", 8)).pack(anchor='w', padx=20)
        
        # دکمه مهم برای نمایش/مخفی کردن کاور
        chk_cover = tk.Checkbutton(win, text="Show Album Art (Larger Window)", variable=self.var_show_cover, command=self.update_layout, **c_cfg)
        chk_cover.pack(fill=tk.X, padx=20)

    def add_files(self):
        files = filedialog.askopenfilenames(filetypes=[("Audio", "*.mp3 *.wav")])
        if not files: return
        for f in files:
            name = os.path.splitext(os.path.basename(f))[0]
            self.playlist_data.append({'path': f, 'name': name})
            self.listbox.insert(tk.END, name)
        
        if self.current_index == -1: self.play_track(0)
        self.btn_add.pack_forget() # مخفی کردن دکمه افزودن

    def play_track(self, index):
        if 0 <= index < len(self.playlist_data):
            if self.channel: self.channel.stop()
            self.current_index = index
            data = self.playlist_data[index]
            try:
                self.current_sound = pygame.mixer.Sound(data['path'])
                self.channel = self.current_sound.play(loops=-1)
                self.track_duration = self.current_sound.get_length()
                
                self.start_time = time.time(); self.total_pause_duration = 0
                self.is_playing = True; self.is_paused = False
                
                self.btn_play.config(text="⏸")
                self.lbl_track.config(text=data['name'])
                self.lbl_header_title.config(text=f"Playing: {data['name'][:20]}...")
                self.p_bar.config(to=self.track_duration)
                
                self.listbox.selection_clear(0, tk.END)
                self.listbox.selection_set(index)
                self.listbox.see(index)
            except Exception as e: print(e)

    def toggle_play_pause(self):
        if self.channel:
            if self.is_paused:
                self.channel.unpause(); self.is_paused = False
                self.total_pause_duration += (time.time() - self.pause_start_time)
                self.btn_play.config(text="⏸")
            else:
                self.channel.pause(); self.is_paused = True
                self.pause_start_time = time.time()
                self.btn_play.config(text="▶")
        elif self.playlist_data: self.play_track(0)

    def next_track(self):
        if self.playlist_data: self.play_track((self.current_index + 1) % len(self.playlist_data))
    def prev_track(self):
        if self.playlist_data: self.play_track((self.current_index - 1) % len(self.playlist_data))
    def on_list_click(self, e):
        if self.listbox.curselection(): self.play_track(self.listbox.curselection()[0])

    def format_time(self, s): return f"{int(s//60):02}:{int(s%60):02}"

    def process_audio_logic(self):
        try:
            if self.is_playing and self.channel and not self.is_paused:
                elapsed = time.time() - self.start_time - self.total_pause_duration
                if elapsed > self.track_duration: self.next_track()
                else:
                    self.seek_var.set(elapsed)
                    self.lbl_time.config(text=f"{self.format_time(elapsed)} / {self.format_time(self.track_duration)}")

                # SPATIAL LOGIC
                screen_w = self.root.winfo_screenwidth()
                screen_h = self.root.winfo_screenheight()
                
                if self.var_mouse.get(): in_x, in_y = self.root.winfo_pointerxy()
                else:
                    win_w = self.root.winfo_width()
                    win_h = self.root.winfo_height()
                    in_x = self.root.winfo_x() + (win_w / 2)
                    in_y = self.root.winfo_y() + (win_h / 2)

                left_vol = 1.0; right_vol = 1.0
                if self.var_pan.get():
                    ratio = max(0.0, min(1.0, in_x / screen_w))
                    left_vol = (1.0 - ratio) ** 1.5
                    right_vol = ratio ** 1.5

                vert_factor = 1.0
                if self.var_vert.get():
                    ratio_y = max(0.0, min(1.0, in_y / screen_h))
                    vert_factor = (1.0 - ratio_y) ** 0.8
                
                if self.var_min_fx.get() and self.root.state() == 'iconic': vert_factor = 0.1
                
                self.channel.set_volume(left_vol * vert_factor, right_vol * vert_factor)
        except: pass
        self.root.after(30, self.process_audio_logic)

if __name__ == "__main__":
    try:
        root = tk.Tk()
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except: pass
        app = CompactSpatialPlayer(root)
        root.mainloop()
    except Exception as e:
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")