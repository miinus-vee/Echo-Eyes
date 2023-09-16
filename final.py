import wx
import threading
import pytesseract
import pyttsx3
import pyautogui
import time
import sys

# Initialize text-to-speech engine
engine = pyttsx3.init()
voices = engine.getProperty("voices")
volume = 0.5  # Default volume
rate = 200  # Default speech rate (words per minute)
current_voice = voices[0]  # Default voice
current_language = "eng"  # Default language (English)

# Store the previous cursor position
previous_cursor_position = pyautogui.position()

# Variable to control the main loop
running = False


class MyFrame(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, size=(1300, 1000))

        # Set the favicon (replace 'Logo.png' with the actual path)
        icon = wx.Icon("Logo.png", wx.BITMAP_TYPE_PNG)
        self.SetIcon(icon)

        # Create a notebook for tabs
        notebook = wx.Notebook(self)
        self.panel1 = wx.Panel(notebook)
        self.panel2 = wx.Panel(notebook)

        notebook.AddPage(self.panel2, "Settings")
        notebook.AddPage(self.panel1, "Instructions")

        # Instructions tab
        instructions_text = (
            "Welcome to EchoEYES!\n\n"
            "Instructions:\n\n"
            "1. Select the desired language from the dropdown (English or Hindi).\n"
            "2. Adjust the volume and speech rate using the sliders.\n"
            "3. Choose a voice from the available options.\n"
            "4. Click 'Launch' to start the text-to-speech application.\n"
            "5. Click 'Quit' to exit the application.\n"
            "6. Move your cursor to different text on the screen to hear it spoken.\n"
        )
        self.instructions_label = wx.StaticText(self.panel1, label=instructions_text)

        # Logo image on the Instructions tab
        self.logo_bitmap_instructions = wx.Bitmap("Logo.png", wx.BITMAP_TYPE_PNG)
        self.logo_staticbitmap_instructions = wx.StaticBitmap(
            self.panel1,
            wx.ID_ANY,
            self.logo_bitmap_instructions,
            wx.DefaultPosition,
            wx.DefaultSize,
        )

        # Add logo and instructions label to a sizer
        instructions_sizer = wx.BoxSizer(wx.VERTICAL)
        instructions_sizer.Add(
            self.logo_staticbitmap_instructions,
            flag=wx.ALIGN_CENTER | wx.ALL,
            border=10,
        )
        instructions_sizer.Add(
            self.instructions_label, flag=wx.ALIGN_CENTER | wx.ALL, border=10
        )

        # Set the sizer for the Instructions tab
        self.panel1.SetSizer(instructions_sizer)

        # Settings tab
        panel = self.panel2
        vbox = wx.BoxSizer(wx.VERTICAL)

        # Load the logo image
        self.logo_bitmap = wx.Bitmap("Logo.png", wx.BITMAP_TYPE_PNG)

        # Create a StaticBitmap widget to display the logo
        self.logo_staticbitmap = wx.StaticBitmap(
            panel, wx.ID_ANY, self.logo_bitmap, wx.DefaultPosition, wx.DefaultSize
        )
        vbox.Add(self.logo_staticbitmap, flag=wx.ALIGN_CENTER | wx.ALL, border=10)

        # Language selection
        language_label = wx.StaticText(panel, label="Select Language:")
        self.language_dropdown = wx.Choice(panel, choices=["English", "Hindi"])
        self.Bind(wx.EVT_CHOICE, self.on_language_select, self.language_dropdown)
        vbox.Add(language_label, flag=wx.ALIGN_CENTER | wx.ALL, border=10)
        vbox.Add(self.language_dropdown, flag=wx.EXPAND | wx.ALL, border=10)

        # Increase the size of the buttons
        button_size = wx.Size(200, 60)
        launch_button = wx.Button(panel, label="Launch", size=button_size)
        quit_button = wx.Button(panel, label="Quit", size=button_size)
        vbox.Add(launch_button, flag=wx.ALIGN_CENTER | wx.ALL, border=10)
        vbox.Add(quit_button, flag=wx.ALIGN_CENTER | wx.ALL, border=10)

        self.Bind(wx.EVT_BUTTON, self.on_launch, launch_button)
        self.Bind(wx.EVT_BUTTON, self.on_quit, quit_button)

        # Volume slider
        volume_label = wx.StaticText(panel, label="Volume:")
        self.volume_slider = wx.Slider(
            panel,
            value=int(volume * 100),
            minValue=0,
            maxValue=100,
            style=wx.SL_HORIZONTAL,
        )
        self.Bind(wx.EVT_SLIDER, self.on_volume_change, self.volume_slider)
        vbox.Add(volume_label, flag=wx.ALIGN_CENTER | wx.ALL, border=10)
        vbox.Add(self.volume_slider, flag=wx.EXPAND | wx.ALL, border=10)

        # Rate slider
        rate_label = wx.StaticText(panel, label="Speech Rate:")
        self.rate_slider = wx.Slider(
            panel, value=rate, minValue=100, maxValue=400, style=wx.SL_HORIZONTAL
        )
        self.Bind(wx.EVT_SLIDER, self.on_rate_change, self.rate_slider)
        vbox.Add(rate_label, flag=wx.ALIGN_CENTER | wx.ALL, border=10)
        vbox.Add(self.rate_slider, flag=wx.EXPAND | wx.ALL, border=10)

        # Voice selection
        voice_label = wx.StaticText(panel, label="Select Voice:")
        voice_choices = [voice.name for voice in voices]
        self.voice_dropdown = wx.ComboBox(
            panel, choices=voice_choices, style=wx.CB_READONLY
        )
        self.Bind(wx.EVT_COMBOBOX, self.on_voice_select, self.voice_dropdown)
        vbox.Add(voice_label, flag=wx.ALIGN_CENTER | wx.ALL, border=10)
        vbox.Add(self.voice_dropdown, flag=wx.EXPAND | wx.ALL, border=10)

        panel.SetSizer(vbox)

    def on_launch(self, event):
        start_main_loop()
        self.Iconize(True)

    def on_quit(self, event):
        stop_main_loop()
        wx.CallAfter(self.Close)

    def on_volume_change(self, event):
        global volume
        volume = self.volume_slider.GetValue() / 100

    def on_rate_change(self, event):
        global rate
        rate = self.rate_slider.GetValue()

    def on_voice_select(self, event):
        global current_voice
        selected_voice_name = self.voice_dropdown.GetValue()
        for voice in voices:
            if voice.name == selected_voice_name:
                current_voice = voice
                break

    def on_language_select(self, event):
        global current_language
        selected_language = self.language_dropdown.GetStringSelection()
        if selected_language == "English":
            current_language = "eng"
        elif selected_language == "Hindi":
            current_language = "hin"


def take_screenshot():
    # Capture a screenshot of the entire screen
    screenshot = pyautogui.screenshot()
    cursor_position = pyautogui.position()

    # Determine the region of interest around the cursor position
    x, y = cursor_position
    region = (x, y - 20, x + 250, y + 20)
    region_image = screenshot.crop(region)
    region_image_gray = region_image.convert("L")
    region_image_gray = region_image.convert("L")
    extracted_text = pytesseract.image_to_string(region_image_gray, lang="eng+hin")

    sys.stdout.reconfigure(encoding="utf-8")
    return extracted_text


def detect_screen_change(previous_text):
    global previous_cursor_position
    current_cursor_position = pyautogui.position()

    # Check if the cursor has moved from its previous position
    if current_cursor_position != previous_cursor_position:
        # Capture a new screenshot and perform OCR
        new_text = take_screenshot()

        # Compare the text extracted from the current and previous screenshots
        if new_text != previous_text:
            # If the text has changed, alert the user
            # If the text has changed, alert the user
            engine.stop()
            print(new_text)
            speak_text(new_text)

        previous_cursor_position = current_cursor_position
        return new_text
    else:
        return previous_text


def speak_text(text):
    engine.setProperty("volume", volume)
    engine.setProperty("rate", rate)
    engine.setProperty("voice", current_voice.id)
    engine.say(text)
    engine.runAndWait()


def main_loop():
    global running
    initial_text = take_screenshot()

    while running:
        # Check for cursor movement and screen change
        initial_text = detect_screen_change(initial_text)
        time.sleep(0.5)


def start_main_loop():
    global running
    running = True
    threading.Thread(target=main_loop).start()


def stop_main_loop():
    global running
    running = False


app = wx.App()
frame = MyFrame(None, -1, "EchoEYES")
frame.Show()
app.MainLoop()
