import tkinter as tk
import tkinter.messagebox as messagebox
import tkinter.colorchooser as colorchooser
import tkinter.filedialog as filedialog
import tkinter.font as tkfont
import tkinter.ttk as ttk
import psutil
import threading
import time
import json
import os
import sys
from pathlib import Path

# --- PyInstaller Resource Handling ---
def resource_path(relative_path):
    """ Get absolute path to a resource, works for dev and for PyInstaller. """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        # Not running in a PyInstaller bundle, use the script's directory
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

# --- Dependency Checks ---
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import winreg
    WINDOWS_REGISTRY_AVAILABLE = True
except ImportError:
    WINDOWS_REGISTRY_AVAILABLE = False

class NetworkOverlay:
    """A customizable desktop network monitoring tool."""

    def __init__(self):
        # --- Single Instance Check ---
        self.lock_file = Path(os.path.expanduser("~")) / ".network_overlay.lock"
        if not self._check_single_instance():
            messagebox.showerror("Error", "Network Overlay is already running!")
            sys.exit(1)
        self._create_lock_file()

        # --- Resource Paths Setup ---
        self._setup_resources()

        # --- Main Window Initialization ---
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.title("Network Overlay")

        self._set_window_icon()

        # --- Configuration and Variables ---
        self._load_configuration()
        self._initialize_variables()
        self._setup_themes()

        # --- UI and Events ---
        self.setup_ui()

        # --- Network Monitoring ---
        self._initialize_network_counters()

        # --- Start Background Threads ---
        self.update_running = True
        self._start_threads()

        # --- Finalize ---
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    # --- Initialization Methods ---
    def _setup_resources(self):
        """Define paths for icons using the resource_path helper."""
        self.ICON_ICO_PATH = resource_path("icon.ico")
        self.ICON_PNG_PATH = resource_path("icon.png")

    def _set_window_icon(self):
        """Sets the application icon for the window title bar and taskbar."""
        try:
            if os.path.exists(self.ICON_ICO_PATH):
                self.root.iconbitmap(self.ICON_ICO_PATH)
            elif PIL_AVAILABLE and os.path.exists(self.ICON_PNG_PATH):
                self.icon_image = tk.PhotoImage(file=self.ICON_PNG_PATH)
                self.root.iconphoto(True, self.icon_image)
        except Exception as e:
            print(f"Warning: Could not set window icon. {e}")

    def _load_configuration(self):
        self.config_file = Path(os.path.expanduser("~")) / ".network_overlay_config.json"
        defaults = {"theme":"modern","positioning":"free","x":50,"y":None,"update_interval":1,"custom_bg":"#FF5733","custom_fg":"#FFFFFF","custom_font":"Arial","custom_size":10,"custom_style":"normal","custom_border":1,"custom_relief":"flat","custom_opacity":0.9,"up_icon":"↑","down_icon":"↓","background_image":None,"always_on_top":True,"auto_start":False}
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f: data = json.load(f)
                defaults.update(data)
            except Exception as e: print(f"Config load error: {e}")
        self.config = defaults

    def _initialize_variables(self):
        self.current_theme = self.config.get("theme", "modern")
        self.positioning_mode = self.config.get("positioning", "free")
        self.update_interval = self.config.get("update_interval", 1)
        self.dragging, self.start_x, self.start_y = False, 0, 0
        self.label, self.main_frame, self.context_menu = None, None, None

    def _setup_themes(self):
        self.themes = {
            "modern": {"bg":"#2D2D2D","fg":"#FFFFFF","font":("Segoe UI",10,"bold"),"border":1,"relief":"flat","transparency":"#2D2D2D","opacity":0.9},
            "glass":  {"bg":"#000000","fg":"#00FF00","font":("Consolas",9),"border":0,"relief":"flat","transparency":"#000000","opacity":0.8},
            "neon":   {"bg":"#0A0A0A","fg":"#00FFFF","font":("Arial",10,"bold"),"border":2,"relief":"raised","transparency":"#0A0A0A","opacity":0.95},
            "classic":{"bg":"SystemButtonFace","fg":"SystemButtonText","font":("TkDefaultFont",9),"border":1,"relief":"raised","transparency":None,"opacity":1.0},
            "dark_pro":{"bg":"#1E1E1E","fg":"#D4D4D4","font":("Cascadia Code",9),"border":1,"relief":"solid","transparency":"#1E1E1E","opacity":0.92},
            "customizable":{
                "bg":self.config.get("custom_bg"), "fg":self.config.get("custom_fg"),
                "font":(self.config.get("custom_font"),self.config.get("custom_size"),self.config.get("custom_style")),
                "border":self.config.get("custom_border"),"relief":self.config.get("custom_relief"),
                "opacity":self.config.get("custom_opacity"), "transparency":self.config.get("custom_bg"),
                "up_icon":self.config.get("up_icon"),"down_icon":self.config.get("down_icon"),
                "background_image":self.config.get("background_image"),
            }
        }
    
    def _initialize_network_counters(self):
        try:
            net_io = psutil.net_io_counters()
            self.prev_bytes_sent, self.prev_bytes_recv = net_io.bytes_sent, net_io.bytes_recv
        except Exception:
            self.prev_bytes_sent, self.prev_bytes_recv = 0, 0
            
    def _start_threads(self):
        threading.Thread(target=self.update_throughput, daemon=True).start()
        threading.Thread(target=self.maintain_topmost, daemon=True).start()

    # --- UI Setup ---
    def setup_ui(self):
        for widget in self.root.winfo_children(): widget.destroy()
        theme = self.themes[self.current_theme]

        if theme.get("transparency"): self.root.attributes("-transparentcolor", theme["transparency"])
        try: self.root.attributes("-alpha", theme["opacity"])
        except tk.TclError: pass

        bg_color = theme["bg"] if theme["bg"] != "SystemButtonFace" else self.root.cget("bg")
        self.root.config(bg=bg_color)
        
        self.main_frame = tk.Frame(self.root, bg=bg_color, bd=theme["border"], relief=theme["relief"])
        self.main_frame.pack(fill="both", expand=True)
        text = f"{theme.get('up_icon', '↑')}: 0.0 B/s\n{theme.get('down_icon', '↓')}: 0.0 B/s"
        
        self.label = tk.Label(self.main_frame, text=text, font=theme["font"], fg=theme["fg"], bg=bg_color, justify="left")
        self.label.pack(padx=5, pady=2)
        
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.setup_context_menu()
        self.setup_events()
        self.position_overlay()

    def setup_context_menu(self):
        menu=self.context_menu; menu.delete(0,"end")
        pos_menu=tk.Menu(menu,tearoff=0)
        positions = [("Free Movement","free"),("Bottom Left","bottom_left"),("Bottom Middle","bottom_middle"),("Bottom Right","bottom_right"),("Top Left","top_left"),("Top Right","top_right"),("Center","center")]
        for lbl,mode in positions: pos_menu.add_command(label=lbl,command=lambda m=mode:self.set_positioning(m))
        menu.add_cascade(label="Position",menu=pos_menu)

        theme_menu=tk.Menu(menu,tearoff=0)
        for t in self.themes: theme_menu.add_command(label=t.replace("_"," ").title(),command=lambda th=t:self.change_theme(th))
        menu.add_cascade(label="Themes",menu=theme_menu)

        settings_menu=tk.Menu(menu,tearoff=0)
        settings_menu.add_command(label="Update Interval...",command=self.set_update_interval)
        settings_menu.add_command(label="Opacity...",command=self.set_opacity)
        settings_menu.add_command(label="Toggle Always On Top",command=self.toggle_always_on_top)
        if WINDOWS_REGISTRY_AVAILABLE: settings_menu.add_command(label="Toggle Auto Start",command=self.toggle_auto_start)
        menu.add_cascade(label="Settings",menu=settings_menu)
        
        if self.current_theme=="customizable":
            cust_menu=tk.Menu(menu,tearoff=0)
            cust_menu.add_command(label="Colors...",command=self.customize_colors)
            cust_menu.add_command(label="Icons & Text...",command=self.customize_icons) # Restored
            cust_menu.add_command(label="Font & Style...",command=self.customize_font) # Restored
            cust_menu.add_command(label="Background Image...",command=self.set_background) # Restored
            cust_menu.add_command(label="Border & Effects...",command=self.customize_border) # Restored
            cust_menu.add_separator()
            cust_menu.add_command(label="Reset to Default",command=self.reset_customization)
            menu.add_cascade(label="Customize",menu=cust_menu)
            
        menu.add_separator()
        menu.add_command(label="About",command=self.show_about)
        menu.add_command(label="Exit",command=self.on_closing)

    def setup_events(self):
        for widget in [self.root, self.main_frame, self.label]:
            if widget:
                widget.bind("<Button-1>",self.start_drag)
                widget.bind("<B1-Motion>",self.drag)
                widget.bind("<ButtonRelease-1>",self.stop_drag)
                widget.bind("<Button-3>",self.show_context_menu)

    def position_overlay(self):
        self.root.update_idletasks()
        sw,sh = self.root.winfo_screenwidth(),self.root.winfo_screenheight()
        ww,wh = self.root.winfo_reqwidth(),self.root.winfo_reqheight()
        mode, x, y = self.positioning_mode, 0, 0
        
        if mode == "free": x,y = self.config.get("x",50),self.config.get("y",sh-wh-50)
        elif mode == "bottom_left": x,y = 0, sh - wh
        elif mode == "bottom_middle": x,y = (sw - ww) // 2, sh - wh
        elif mode == "bottom_right": x,y = sw - ww, sh - wh
        elif mode == "top_left": x,y = 0, 0
        elif mode == "top_right": x,y = sw - ww, 0
        elif mode == "center": x,y = (sw - ww) // 2, (sh - wh) // 2
        
        x, y = max(0, min(x, sw-ww)), max(0, min(y, sh-wh))
        self.root.geometry(f"+{int(x)}+{int(y)}")

    def change_theme(self, theme_name):
        self.current_theme = theme_name
        self.config["theme"] = theme_name
        if theme_name == "customizable": self._setup_themes()
        self.save_config(); self.setup_ui()

    # --- Core Functionality ---
    def maintain_topmost(self):
        while self.update_running:
            try:
                if self.config.get("always_on_top", True): self.root.attributes("-topmost", True)
                time.sleep(1)
            except tk.TclError: break

    def update_throughput(self):
        while self.update_running:
            try:
                io = psutil.net_io_counters()
                sent_s = (io.bytes_sent - self.prev_bytes_sent) / self.update_interval
                recv_s = (io.bytes_recv - self.prev_bytes_recv) / self.update_interval
                self.prev_bytes_sent, self.prev_bytes_recv = io.bytes_sent, io.bytes_recv
                
                theme = self.themes[self.current_theme]
                up_icon = theme.get('up_icon','↑') if self.current_theme == "customizable" else "Up:"
                down_icon = theme.get('down_icon','↓') if self.current_theme == "customizable" else "Dn:"
                text = f"{up_icon} {self.format_speed(sent_s)}\n{down_icon} {self.format_speed(recv_s)}"
                self.root.after(0, lambda: self.safe_update_label(text))
            except Exception: break
            time.sleep(self.update_interval)

    def format_speed(self, s):
        if s<1024: return f"{s:.1f} B/s"
        if s<1024**2: return f"{s/1024:.1f} KB/s"
        if s<1024**3: return f"{s/1024**2:.1f} MB/s"
        return f"{s/1024**3:.1f} GB/s"

    def safe_update_label(self, text):
        try:
            if self.label and self.label.winfo_exists(): self.label.config(text=text)
        except tk.TclError: pass

    # --- Event Handlers ---
    def start_drag(self, e):
        if self.positioning_mode=="free": self.dragging=True; self.start_x,self.start_y = e.x, e.y
    def drag(self, e):
        if self.dragging: self.root.geometry(f"+{self.root.winfo_x()+e.x-self.start_x}+{self.root.winfo_y()+e.y-self.start_y}")
    def stop_drag(self, e):
        if self.dragging: self.dragging=False; self.save_config()
    def show_context_menu(self, e):
        try: self.context_menu.tk_popup(e.x_root,e.y_root)
        finally: self.context_menu.grab_release()
    def set_positioning(self, m):
        self.positioning_mode=m; self.config["positioning"]=m; self.position_overlay(); self.save_config()

    # --- Settings and Customization Dialogs (Restored) ---
    def set_update_interval(self):
        d=tk.Toplevel(self.root); d.title("Update Interval"); d.transient(self.root); d.grab_set()
        tk.Label(d,text="Interval (0.1–10s):").pack(pady=5)
        iv=tk.StringVar(value=str(self.update_interval))
        tk.Entry(d,textvariable=iv).pack(pady=5)
        def a():
            try:
                v=float(iv.get());
                if 0.1<=v<=10: self.update_interval=v;self.config["update_interval"]=v;self.save_config();d.destroy()
                else: messagebox.showerror("Error","Must be 0.1–10", parent=d)
            except: messagebox.showerror("Error","Invalid", parent=d)
        tk.Button(d,text="Apply",command=a).pack(pady=5); d.geometry("250x120")

    def set_opacity(self):
        d=tk.Toplevel(self.root); d.title("Opacity"); d.transient(self.root); d.grab_set()
        tk.Label(d,text="Opacity (0.1–1.0):").pack(pady=5)
        ov=tk.DoubleVar(value=self.themes[self.current_theme]["opacity"])
        tk.Scale(d,from_=0.1,to=1.0,resolution=0.05,orient="horizontal",variable=ov).pack(pady=5,fill="x",padx=20)
        def a():
            v=ov.get(); self.themes[self.current_theme]["opacity"]=v
            if self.current_theme=="customizable": self.config["custom_opacity"]=v
            try: self.root.attributes("-alpha",v)
            except: pass
            self.save_config(); d.destroy()
        tk.Button(d,text="Apply",command=a).pack(pady=10); d.geometry("300x150")
        
    def _choose_color(self, var, btn, title):
        color = colorchooser.askcolor(title=f"Choose {title}", color=var[0])[1]
        if color: var[0] = color; btn.config(bg=color)

    def customize_colors(self):
        d=tk.Toplevel(self.root); d.title("Customize Colors"); d.transient(self.root); d.grab_set()
        bg_var=[self.config.get("custom_bg")]; fg_var=[self.config.get("custom_fg")]
        tk.Label(d,text="Background Color:").pack(pady=5)
        b1=tk.Button(d,text="Choose",bg=bg_var[0],width=20,command=lambda:self._choose_color(bg_var,b1,"Background"));b1.pack(pady=5)
        tk.Label(d,text="Text Color:").pack(pady=5)
        b2=tk.Button(d,text="Choose",bg=fg_var[0],width=20,command=lambda:self._choose_color(fg_var,b2,"Text"));b2.pack(pady=5)
        def apply_changes():
            self.config.update({"custom_bg": bg_var[0], "custom_fg": fg_var[0]})
            self.save_config(); d.destroy()
            if self.current_theme == "customizable": self.change_theme("customizable")
        tk.Button(d, text="Apply", command=apply_changes).pack(pady=15); d.geometry("350x220")

    def customize_icons(self):
        d=tk.Toplevel(self.root); d.title("Customize Icons & Text"); d.transient(self.root); d.grab_set()
        tk.Label(d,text="Up Icon:").pack(pady=5)
        ue=tk.Entry(d,font=("Arial",12),width=10); ue.pack(); ue.insert(0,self.config.get("up_icon","↑"))
        tk.Label(d,text="Down Icon:").pack(pady=5)
        de=tk.Entry(d,font=("Arial",12),width=10); de.pack(); de.insert(0,self.config.get("down_icon","↓"))
        suggestions=[("↑↓","↑","↓"),("⬆⬇","⬆","⬇"),("📤📥","📤","📥"),("🔼🔽","🔼","🔽")]
        sf=tk.Frame(d); sf.pack(pady=10)
        for i,(lbl,u,dn) in enumerate(suggestions):
            cmd=lambda u=u,dn=dn:(ue.delete(0,tk.END),ue.insert(0,u),de.delete(0,tk.END),de.insert(0,dn))
            tk.Button(sf,text=lbl,command=cmd,font=("Arial",12),width=6).grid(row=0,column=i,padx=2)
        def a():
            u,v=ue.get()or"↑",de.get()or"↓"; self.config["up_icon"],self.config["down_icon"]=u,v
            self.save_config(); d.destroy();
            if self.current_theme=="customizable":self.change_theme("customizable")
        tk.Button(d,text="Apply",command=a).pack(pady=10); d.geometry("350x250")

    def customize_font(self):
        d=tk.Toplevel(self.root); d.title("Customize Font & Style"); d.transient(self.root); d.grab_set()
        tk.Label(d,text="Font Family:").pack(pady=5); fv=tk.StringVar(value=self.config.get("custom_font","Arial"))
        ttk.Combobox(d,textvariable=fv,values=sorted(tkfont.families())).pack(pady=5)
        tk.Label(d,text="Font Size:").pack(pady=5); sv=tk.IntVar(value=self.config.get("custom_size",10))
        tk.Scale(d,from_=6,to=24,orient="horizontal",variable=sv).pack(pady=5,fill="x",padx=20)
        tk.Label(d,text="Style:").pack(pady=5); sv2=tk.StringVar(value=self.config.get("custom_style","normal"))
        f2=tk.Frame(d); f2.pack(pady=5)
        for t,v in [("Normal","normal"),("Bold","bold"),("Italic","italic"),("Bold Italic","bold italic")]:
            tk.Radiobutton(f2,text=t,variable=sv2,value=v).pack(side="left",padx=5)
        def a():
            self.config.update({"custom_font":fv.get(),"custom_size":sv.get(),"custom_style":sv2.get()})
            self.save_config(); d.destroy();
            if self.current_theme=="customizable": self.change_theme("customizable")
        tk.Button(d,text="Apply",command=a).pack(pady=15); d.geometry("400x320")

    def customize_border(self):
        d=tk.Toplevel(self.root); d.title("Border & Effects"); d.transient(self.root); d.grab_set()
        tk.Label(d,text="Border Width:").pack(pady=5); bv=tk.IntVar(value=self.config.get("custom_border",1))
        tk.Scale(d,from_=0,to=5,orient="horizontal",variable=bv).pack(pady=5,fill="x",padx=20)
        tk.Label(d,text="Border Style:").pack(pady=5); rv=tk.StringVar(value=self.config.get("custom_relief","flat"))
        f2=tk.Frame(d); f2.pack(pady=5)
        for i,r in enumerate(["flat","raised","sunken","solid","ridge","groove"]):
            tk.Radiobutton(f2,text=r.title(),variable=rv,value=r).grid(row=i//3,column=i%3,sticky="w")
        def a():
            self.config.update({"custom_border":bv.get(),"custom_relief":rv.get()})
            self.save_config(); d.destroy();
            if self.current_theme=="customizable": self.change_theme("customizable")
        tk.Button(d,text="Apply",command=a).pack(pady=15); d.geometry("350x280")
    
    def set_background(self):
        fp = filedialog.askopenfilename(title="Select Background Image", filetypes=[("Image files","*.png *.jpg *.jpeg")])
        if fp:
            self.config["background_image"]=fp; self.save_config()
            if self.current_theme=="customizable": self.change_theme("customizable")

    def reset_customization(self):
        if messagebox.askyesno("Reset","Reset all customizations to default?"):
            defaults={"custom_bg":"#FF5733","custom_fg":"#FFFFFF","custom_font":"Arial","custom_size":10,"custom_style":"normal","custom_border":1,"custom_relief":"flat","custom_opacity":0.9,"up_icon":"↑","down_icon":"↓","background_image":None}
            self.config.update(defaults); self.save_config()
            if self.current_theme=="customizable": self.change_theme("customizable")
    
    # --- System Integration and Cleanup ---
    def toggle_always_on_top(self):
        new_state = not self.config.get("always_on_top", True)
        self.config["always_on_top"] = new_state
        self.root.attributes("-topmost", new_state); self.save_config()
        
    def show_about(self):
        messagebox.showinfo("About Network Overlay", "Network Overlay v2.1\nA customizable desktop network monitor.\n\nDeveloper: kndnsow")

    def toggle_auto_start(self):
        if not WINDOWS_REGISTRY_AVAILABLE: return messagebox.showerror("Error", "Auto-start is only on Windows.")
        is_enabled = self.config.get("auto_start", False)
        try:
            if is_enabled: self._remove_from_startup(); messagebox.showinfo("Success", "Auto-start disabled.")
            else: self._add_to_startup(); messagebox.showinfo("Success", "Auto-start enabled.")
            self.config["auto_start"]=not is_enabled; self.save_config()
        except Exception as e: messagebox.showerror("Error", f"Failed to update registry: {e}")

    def _get_executable_path(self):
        return sys.executable if getattr(sys,'frozen',False) else f'"{sys.executable}" "{os.path.abspath(__file__)}"'

    def _add_to_startup(self):
        key_path=r"Software\Microsoft\Windows\CurrentVersion\Run"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER,key_path,0,winreg.KEY_SET_VALUE) as k:
            winreg.SetValueEx(k,"NetworkOverlay",0,winreg.REG_SZ,self._get_executable_path())

    def _remove_from_startup(self):
        key_path=r"Software\Microsoft\Windows\CurrentVersion\Run"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER,key_path,0,winreg.KEY_SET_VALUE) as k:
            try: winreg.DeleteValue(k,"NetworkOverlay")
            except FileNotFoundError: pass

    def on_closing(self):
        self.update_running = False; self.save_config()
        if self.lock_file.exists():
            try: self.lock_file.unlink()
            except OSError: pass
        self.root.destroy()
    
    def save_config(self):
        try:
            if self.root.winfo_exists(): self.config["x"], self.config["y"] = self.root.winfo_x(), self.root.winfo_y()
            with open(self.config_file, 'w') as f: json.dump(self.config, f, indent=2)
        except Exception: pass
            
    def _check_single_instance(self):
        if self.lock_file.exists():
            try:
                if psutil.pid_exists(int(self.lock_file.read_text())): return False
            except Exception: pass
        return True

    def _create_lock_file(self):
        try: self.lock_file.write_text(str(os.getpid()))
        except IOError: pass

if __name__ == "__main__":
    try:
        NetworkOverlay()
    except Exception as e:
        with open("network_overlay_crash.log", "a") as f: f.write(f"{time.ctime()}: {e}\n")
        messagebox.showerror("Fatal Error", f"An unexpected error occurred: {e}")
        sys.exit(1)