# Network Overlay for Taskbar

This project is a Python application that displays live internet upload and download speeds as an overlay on the taskbar. The overlay remains fixed at the bottom-left corner of the screen and stays visible above all other windows, including the taskbar.

## Features

- **Live Network Monitoring**: Displays upload (Up) and download (Dn) speeds in real-time.
- **Taskbar Integration**: The overlay sticks to the bottom-left corner of the screen.
- **Always on Top**: Ensures the overlay is always visible and does not disappear behind other windows or the taskbar.
- **Transparent Background**: Uses a black transparent background for a seamless overlay experience.
- **Lightweight**: Minimal resource usage for continuous monitoring.

---

### Snapshot
![Screenshot 2025-01-22 122143](https://github.com/user-attachments/assets/b6b939bf-e02b-4ce0-8460-be6107e37712)


### Download

Click the link below to get the latest version of the Network Overlay executable:

[Download Network Overlay (.exe)](https://github.com/kndnsow/internet-speed-meter/tree/main/dist)

## Requirements

### Python Libraries

- `tkinter` (Standard Python library for GUI)
- `psutil` (For monitoring network I/O)

To install `psutil`, use:
```bash
pip install psutil
```

### Optional Libraries

- `PyInstaller` (To convert the script into an executable file)

To install `PyInstaller`, use:
```bash
pip install pyinstaller
```

---

## Usage

1. **Run the Script**:
   Save the provided Python script (`network_overlay.py`) to your local machine. Run it using:
   ```bash
   python network_overlay.py
   ```

2. **Overlay Behavior**:
   - The overlay will appear at the bottom-left corner of your screen.
   - It will display upload and download speeds in kilobytes per second (KB/s).
   - It will stay on top of all other windows, including the taskbar.

3. **Quit the Script**:
   - To stop the script, close the terminal running it or use the Task Manager to end the process.

---

## Building the Executable

To run the application without Python, you can create an executable file:

1. Install `PyInstaller`:
   ```bash
   pip install pyinstaller
   ```

2. Create the Executable:
   ```bash
   pyinstaller --onefile --noconsole network_overlay.py
   ```

3. Locate the Executable:
   - The `.exe` file will be available in the `dist` folder.
   - Run the `.exe` file to launch the overlay.

---

## Customization

- **Overlay Position**:
  - Modify the `position_overlay()` method to change the overlay's position.
  - Example:
    ```python
    x_position = 10
    y_position = screen_height - overlay_height - 10
    ```

- **Update Interval**:
  - Adjust the `self.update_interval` value to control how frequently network speeds are updated (default: 1 second).

- **Font and Size**:
  - Customize the font, size, or color in the `tk.Label` definition:
    ```python
    self.label = tk.Label(self.root, font=("Arial", 14), fg="green", bg="black")
    ```

---

## Troubleshooting

- **Overlay Disappears**:
  - Ensure the script is running.
  - The `keep_on_top()` method ensures the overlay stays visible; verify this functionality.

- **Network Speeds Not Updating**:
  - Ensure the `psutil` library is installed.
  - Check your internet connection.

---

## License

This project is open-source and can be used or modified freely for personal or educational purposes.

