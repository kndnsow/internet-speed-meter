import tkinter as tk
import psutil
import threading
import time


class NetworkOverlay:
    def __init__(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)  # Removes window decorations
        self.root.attributes("-transparentcolor", "black")  # Makes black transparent for overlay effect
        self.root.config(bg="black")  # Background set to black for transparency

        self.label = tk.Label(self.root, font=("Arial", 12), fg="white", bg="black")
        self.label.pack()

        # Right-click menu
        self.root.bind("<Button-3>", self.show_close_button)
        self.close_button = tk.Button(self.root, text="Close", command=self.root.destroy)

        self.prev_bytes_sent = psutil.net_io_counters().bytes_sent
        self.prev_bytes_recv = psutil.net_io_counters().bytes_recv
        self.update_interval = 1  # Update every second

        self.position_overlay()

        # Start updating the throughput and keeping the overlay always on top
        threading.Thread(target=self.update_throughput, daemon=True).start()
        threading.Thread(target=self.keep_on_top, daemon=True).start()

        self.root.mainloop()

    def position_overlay(self):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        overlay_width = 200
        overlay_height = 40
        x_position = 0
        y_position = screen_height - overlay_height
        self.root.geometry(f"{overlay_width}x{overlay_height}+{x_position}+{y_position}")

    def keep_on_top(self):
        while True:
            self.root.attributes("-topmost", True)
            time.sleep(0.5)

    def format_speed(self, speed):
        if speed < 1024:
            return f"{speed:.1f} KB/s"
        elif speed < 1024 ** 2:
            return f"{speed / 1024:.1f} MB/s"
        else:
            return f"{speed / (1024 ** 2):.1f} GB/s"

    def update_throughput(self):
        while True:
            current_bytes_sent = psutil.net_io_counters().bytes_sent
            current_bytes_recv = psutil.net_io_counters().bytes_recv
            sent_speed = (current_bytes_sent - self.prev_bytes_sent) / self.update_interval
            recv_speed = (current_bytes_recv - self.prev_bytes_recv) / self.update_interval
            self.prev_bytes_sent = current_bytes_sent
            self.prev_bytes_recv = current_bytes_recv
            formatted_sent = self.format_speed(sent_speed / 1024)
            formatted_recv = self.format_speed(recv_speed / 1024)
            self.label.config(text=f"Up: {formatted_sent}\nDn: {formatted_recv}")
            time.sleep(self.update_interval)

    def show_close_button(self, event):
        self.close_button.place(x=event.x, y=event.y)


if __name__ == "__main__":
    NetworkOverlay()
