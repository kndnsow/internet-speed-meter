
# Customizable Network Speed Overlay

A lightweight, powerful, and highly customizable desktop widget that displays your real-time network upload and download speeds. It uses a clean, modern interface and a simple right-click context menu for all configuration.

![Screenshot](https://github.com/kndnsow/internet-speed-meter/raw/main/Screenshots/Screenshot_0.png)

*The default "Modern" theme. Appearance is fully customizable.*

## Features

- **Live Network Monitoring**: Displays real-time upload and download speeds, intelligently formatted from B/s to GB/s.
- **Extensive Customization**: A dedicated "Customizable" theme allows you to change:
    - **Colors**: Pick any background and text color.
    - **Fonts**: Choose from any font family, size, and style (bold, italic) installed on your system.
    - **Icons**: Replace the default "Up/Down" text or arrows with your favorite emojis or symbols.
    - **Opacity**: Adjust the transparency of the widget from fully opaque to nearly invisible.
    - **Borders**: Set border width and style (e.g., solid, raised, sunken).
- **Multiple Themes**: Comes with several built-in themes like Modern, Glass, Neon, Classic, and a high-contrast Dark Pro.
- **Flexible Positioning**:
    - **Drag & Drop**: Freely move the overlay anywhere on your screen.
    - **Snap Positions**: Instantly snap the widget to corners or center-screen positions.
- **User-Friendly Interface**: All settings are accessed through a clean right-click context menu. No need to edit files for configuration.
- **System Integration**:
    - **Persistent Settings**: Your position, theme, and custom settings are automatically saved and reloaded on startup.
    - **Windows Auto-Start**: An option to automatically launch the application when you log in to Windows.
    - **Always on Top (Toggleable)**: Keep the overlay visible, or turn it off if you prefer.
    - **Single Instance Lock**: Prevents accidentally opening multiple copies of the application.

---

### Download

You can download the latest pre-built version for Windows. No installation is required.

[Download Network Overlay (.exe)](https://github.com/kndnsow/internet-speed-meter/tree/main/dist)

## Usage

1.  **Run the Executable**: Download and run `network_overlay.exe`.
2.  **Right-Click to Configure**: Right-click anywhere on the overlay to open the context menu. From here you can:
    - Change the theme.
    - Adjust the position.
    - Customize colors, fonts, and icons.
    - Change settings like opacity and update speed.
3.  **Move the Overlay**: If "Position" is set to "Free Movement," simply click and drag the overlay to a new location.
4.  **Exit the Application**: Right-click and select "Exit."

---

## Building from Source

If you want to modify the script or build it yourself, follow these steps.

### Requirements

-   **Python 3.x**
-   **Required Libraries**:
    -   `psutil`: For monitoring network I/O.
    -   `Pillow`: For better image handling.

    Install them using pip:
    ```bash
    pip install psutil pillow
    ```

-   **Build Tool**:
    -   `PyInstaller`: To package the script into an executable.

    Install it using pip:
    ```bash
    pip install pyinstaller
    ```

### Build Command

To create a single `.exe` file that includes the necessary icons, navigate to the script's directory in your terminal and run the following command:

```bash
pyinstaller --noconsole --onefile --icon="icon.ico" --add-data "icon.png;." --add-data "icon.ico;." network_overlay.py
```

-   `--noconsole`: Hides the command prompt window when the application runs.
-   `--onefile`: Bundles everything into a single executable file.
-   `--icon="icon.ico"`: Sets the file icon for the `.exe`.
-   `--add-data "source;."`: **(Crucial)** This ensures that the icon files are included in the executable, which is necessary for them to appear correctly.

The final `network_overlay.exe` will be in the `dist` folder.

---

## Troubleshooting

-   **Icon Missing or Errors on Startup**: If you build the executable yourself, ensure you use the full `--add-data` flags in the PyInstaller command to bundle the `icon.ico` and `icon.png` files.
-   **Cannot Run a Second Copy**: This is intentional. The application uses a lock file (`.network_overlay.lock` in your user home directory) to ensure only one instance is running.
-   **Settings Not Saving**: The configuration is saved to `.network_overlay_config.json` in your user home directory. Ensure your system permissions allow the application to write to this file.

---

## License

This project is open-source and free to use, modify, and distribute.