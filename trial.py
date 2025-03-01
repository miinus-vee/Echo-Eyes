GUI.py

import wx
import pyttsx3

class EchoEYESFrame(wx.Frame):
    def __init__(self, parent, id, title, on_launch, on_quit, on_volume_change, on_rate_change, on_voice_select, on_language_select, on_mode_select):
        wx.Frame.__init__(self, parent, id, title, size=(800, 600))

        # Set the favicon (replace 'Logo.png' with the actual path)
        icon = wx.Icon("Logo.png", wx.BITMAP_TYPE_PNG)
        self.SetIcon(icon)

        # Create a notebook for tabs
        notebook = wx.Notebook(self)
        self.panel1 = wx.Panel(notebook)
        self.panel2 = wx.Panel(notebook)

        notebook.AddPage(self.panel1, "Instructions")
        notebook.AddPage(self.panel2, "Settings")

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
            "7. Choose between 'Cursor Reading' and 'Summarization' modes.\n"
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
        self.Bind(wx.EVT_CHOICE, on_language_select, self.language_dropdown)
        vbox.Add(language_label, flag=wx.ALIGN_CENTER | wx.ALL, border=10)
        vbox.Add(self.language_dropdown, flag=wx.EXPAND | wx.ALL, border=10)

        # Mode selection
        mode_label = wx.StaticText(panel, label="Select Mode:")
        self.mode_dropdown = wx.Choice(panel, choices=["Cursor Reading", "Summarization"])
        self.Bind(wx.EVT_CHOICE, on_mode_select, self.mode_dropdown)
        vbox.Add(mode_label, flag=wx.ALIGN_CENTER | wx.ALL, border=10)
        vbox.Add(self.mode_dropdown, flag=wx.EXPAND | wx.ALL, border=10)

        # Increase the size of the buttons
        button_size = wx.Size(200, 60)
        launch_button = wx.Button(panel, label="Launch", size=button_size)
        quit_button = wx.Button(panel, label="Quit", size=button_size)
        vbox.Add(launch_button, flag=wx.ALIGN_CENTER | wx.ALL, border=10)
        vbox.Add(quit_button, flag=wx.ALIGN_CENTER | wx.ALL, border=10)

        self.Bind(wx.EVT_BUTTON, on_launch, launch_button)
        self.Bind(wx.EVT_BUTTON, on_quit, quit_button)

        # Volume slider
        volume_label = wx.StaticText(panel, label="Volume:")
        self.volume_slider = wx.Slider(
            panel,
            value=50,
            minValue=0,
            maxValue=100,
            style=wx.SL_HORIZONTAL,
        )
        self.Bind(wx.EVT_SLIDER, on_volume_change, self.volume_slider)
        vbox.Add(volume_label, flag=wx.ALIGN_CENTER | wx.ALL, border=10)
        vbox.Add(self.volume_slider, flag=wx.EXPAND | wx.ALL, border=10)

        # Rate slider
        rate_label = wx.StaticText(panel, label="Speech Rate:")
        self.rate_slider = wx.Slider(
            panel, value=200, minValue=100, maxValue=400, style=wx.SL_HORIZONTAL
        )
        self.Bind(wx.EVT_SLIDER, on_rate_change, self.rate_slider)
        vbox.Add(rate_label, flag=wx.ALIGN_CENTER | wx.ALL, border=10)
        vbox.Add(self.rate_slider, flag=wx.EXPAND | wx.ALL, border=10)

        # Voice selection
        voice_label = wx.StaticText(panel, label="Select Voice:")
        engine = pyttsx3.init()
        voices = engine.getProperty("voices")
        voice_choices = [voice.name for voice in voices]
        self.voice_dropdown = wx.ComboBox(
            panel, choices=voice_choices, style=wx.CB_READONLY
        )
        self.Bind(wx.EVT_COMBOBOX, on_voice_select, self.voice_dropdown)
        vbox.Add(voice_label, flag=wx.ALIGN_CENTER | wx.ALL, border=10)
        vbox.Add(self.voice_dropdown, flag=wx.EXPAND | wx.ALL, border=10)

        panel.SetSizer(vbox)









-------x----------------------x---------------------x-------------------------x-----------------------x--------------------x-----------------------



import wx
import threading
import pytesseract
import pyttsx3
import pyautogui
import time
import sys
from gui import EchoEYESFrame

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

# Mode selection: 'cursor' for cursor reading, 'summary' for summarization
mode = 'cursor'


def take_screenshot():
    # Capture a screenshot of the entire screen
    screenshot = pyautogui.screenshot()
    cursor_position = pyautogui.position()

    # Determine the region of interest around the cursor position
    x, y = cursor_position
    region = (x - 125, y - 125, x + 125, y + 125)  # Adjusted for dynamic size
    region_image = screenshot.crop(region)
    region_image_gray = region_image.convert("L")
    extracted_text = pytesseract.image_to_string(region_image_gray, lang="eng+hin")

    sys.stdout.reconfigure(encoding="utf-8")
    return extracted_text, region_image


def describe_image(image):
    # Placeholder for image description logic
    # This could be replaced with a more sophisticated image recognition model
    return "Image description not implemented."


def detect_screen_change(previous_text):
    global previous_cursor_position
    current_cursor_position = pyautogui.position()

    # Check if the cursor has moved from its previous position
    if current_cursor_position != previous_cursor_position:
        # Capture a new screenshot and perform OCR
        new_text, region_image = take_screenshot()

        # Compare the text extracted from the current and previous screenshots
        if new_text != previous_text:
            # If the text has changed, alert the user
            engine.stop()
            if new_text.strip():
                print(new_text)
                speak_text(new_text)
            else:
                # Describe the image if no text is found
                description = describe_image(region_image)
                print(description)
                speak_text(description)

        previous_cursor_position = current_cursor_position
        return new_text
    else:
        return previous_text


def summarize_screen():
    # Capture a screenshot of the entire screen
    screenshot = pyautogui.screenshot()
    screenshot_gray = screenshot.convert("L")
    extracted_text = pytesseract.image_to_string(screenshot_gray, lang="eng+hin")

    # Placeholder for summarization logic
    # This could be replaced with a more sophisticated summarization model
    summary = "Summary not implemented."
    return summary


def speak_text(text):
    engine.setProperty("volume", volume)
    engine.setProperty("rate", rate)
    engine.setProperty("voice", current_voice.id)
    engine.say(text)
    engine.runAndWait()


def main_loop():
    global running
    initial_text, _ = take_screenshot()

    while running:
        if mode == 'cursor':
            # Check for cursor movement and screen change
            initial_text = detect_screen_change(initial_text)
        elif mode == 'summary':
            # Summarize the screen content
            summary = summarize_screen()
            print(summary)
            speak_text(summary)
            time.sleep(5)  # Wait before summarizing again

        time.sleep(0.5)


def start_main_loop():
    global running
    running = True
    threading.Thread(target=main_loop).start()


def stop_main_loop():
    global running
    running = False


def on_launch(event):
    start_main_loop()


def on_quit(event):
    stop_main_loop()
    wx.CallAfter(frame.Close)


def on_volume_change(event):
    global volume
    volume = frame.volume_slider.GetValue() / 100


def on_rate_change(event):
    global rate
    rate = frame.rate_slider.GetValue()


def on_voice_select(event):
    global current_voice
    selected_voice_name = frame.voice_dropdown.GetValue()
    for voice in voices:
        if voice.name == selected_voice_name:
            current_voice = voice
            break


def on_language_select(event):
    global current_language
    selected_language = frame.language_dropdown.GetStringSelection()
    if selected_language == "English":
        current_language = "eng"
    elif selected_language == "Hindi":
        current_language = "hin"


def on_mode_select(event):
    global mode
    selected_mode = frame.mode_dropdown.GetStringSelection()
    if selected_mode == "Cursor Reading":
        mode = 'cursor'
    elif selected_mode == "Summarization":
        mode = 'summary'


app = wx.App()
frame = EchoEYESFrame(None, -1, "EchoEYES", on_launch, on_quit, on_volume_change, on_rate_change, on_voice_select, on_language_select, on_mode_select)
frame.Show()
app.MainLoop()

-----------------------------------------------------------------------------------------------------------------------------------------------


python



import pytesseract
import pyautogui
import numpy as np
from PIL import Image

def take_screenshot():
    # Capture a screenshot of the entire screen
    screenshot = pyautogui.screenshot()
    cursor_position = pyautogui.position()

    # Convert the screenshot to a numpy array for processing
    screenshot_np = np.array(screenshot)

    # Use pytesseract to get the bounding boxes of the text
    data = pytesseract.image_to_data(screenshot, lang="eng+hin", output_type=pytesseract.Output.DICT)

    # Initialize variables to find the bounding box of the text
    x_min, y_min, x_max, y_max = float('inf'), float('inf'), float('-inf'), float('-inf')

    # Loop through the detected text boxes
    for i in range(len(data['text'])):
        if int(data['conf'][i]) > 60:  # Confidence threshold
            (x, y, w, h) = (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
            x_min = min(x_min, x)
            y_min = min(y_min, y)
            x_max = max(x_max, x + w)
            y_max = max(y_max, y + h)

    # If no text was found, return empty string
    if x_min == float('inf'):
        return "", screenshot

    # Crop the region of interest based on the detected text bounding box
    region_image = screenshot.crop((x_min, y_min, x_max, y_max))
    region_image_gray = region_image.convert("L")
    extracted_text = pytesseract.image_to_string(region_image_gray, lang="eng+hin")

    sys.stdout.reconfigure(encoding="utf-8")
    return extracted_text, region_image












---------------------------------------------------------------------------------------------------------------------4th--------------






import wx
import threading
import pytesseract
import pyttsx3
import pyautogui
import time
import sys
import numpy as np
import tensorflow as tf
from PIL import Image

# Load the pre-trained model from TensorFlow
model = tf.saved_model.load("path_to_your_model_directory/saved_model")

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

# Mode selection: 'cursor' for cursor reading, 'summary' for summarization
mode = 'cursor'


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
            "7. Choose between 'Cursor Reading' and 'Summarization' modes.\n"
        )
        self.instructions_label = wx.StaticText(self.panel1, label=instructions_text)

        # Add logo and instructions label to a sizer
        instructions_sizer = wx.BoxSizer(wx.VERTICAL)
        instructions_sizer.Add(self.instructions_label, flag=wx.ALIGN_CENTER | wx.ALL, border=10)
        self.panel1.SetSizer(instructions_sizer)

        # Settings tab
        panel = self.panel2
        vbox = wx.BoxSizer(wx.VERTICAL)

        # Language selection
        language_label = wx.StaticText(panel, label="Select Language:")
        self.language_dropdown = wx.Choice(panel, choices=["English", "Hindi"])
        self.Bind(wx.EVT_CHOICE, self.on_language_select, self.language_dropdown)
        vbox.Add(language_label, flag=wx.ALIGN_CENTER | wx.ALL, border=10)
        vbox.Add(self.language_dropdown, flag=wx.EXPAND | wx.ALL, border=10)

        # Mode selection
        mode_label = wx.StaticText(panel, label="Select Mode:")
        self.mode_dropdown = wx.Choice(panel, choices=["Cursor Reading", "Summarization"])
        self.Bind(wx.EVT_CHOICE, self.on_mode_select, self.mode_dropdown)
        vbox.Add(mode_label, flag=wx.ALIGN_CENTER | wx.ALL, border=10)
        vbox.Add(self.mode_dropdown, flag=wx.EXPAND | wx.ALL, border=10)

        # Launch and Quit buttons
        button_size = wx.Size(200, 60)
        launch_button = wx.Button(panel, label="Launch", size=button_size)
        quit_button = wx.Button(panel, label="Quit", size=button_size)
        self.Bind(wx.EVT_BUTTON, self.on_launch, launch_button)
        self.Bind(wx.EVT_BUTTON, self.on_quit, quit_button)
        vbox.Add(launch_button, flag=wx.ALIGN_CENTER | wx.ALL, border=10)
        vbox.Add(quit_button, flag=wx.ALIGN_CENTER | wx.ALL, border=10)

        # Volume slider
        volume_label = wx.StaticText(panel, label="Volume:")
        self.volume_slider = wx.Slider(panel, value=int(volume * 100), minValue=0, maxValue=100, style=wx.SL_HORIZONTAL)
        self.Bind(wx.EVT_SLIDER, self.on_volume_change, self.volume_slider)
        vbox.Add(volume_label, flag=wx.ALIGN_CENTER | wx.ALL, border=10)
        vbox.Add(self.volume_slider, flag=wx.EXPAND | wx.ALL, border=10)

        # Rate slider
        rate_label = wx.StaticText(panel, label="Speech Rate:")
        self.rate_slider = wx.Slider(panel, value=rate, minValue=100, maxValue=400, style=wx.SL_HORIZONTAL)
        self.Bind(wx.EVT_SLIDER, self.on_rate_change, self.rate_slider)
        vbox.Add(rate_label, flag=wx.ALIGN_CENTER | wx.ALL, border=10)
        vbox.Add(self.rate_slider, flag=wx.EXPAND | wx.ALL, border=10)

        # Voice selection
        voice_label = wx.StaticText(panel, label="Select Voice:")
        voice_choices = [voice.name for voice in voices]
        self.voice_dropdown = wx.ComboBox(panel, choices=voice_choices, style=wx.CB_READONLY)
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

    def on_mode_select(self, event):
        global mode
        selected_mode = self.mode_dropdown.GetStringSelection()
        if selected_mode == "Cursor Reading":
            mode = 'cursor'
        elif selected_mode == "Summarization":
            mode = 'summary'


def detect_objects(image):
    # Convert the image to a tensor
    input_tensor = tf.convert_to_tensor(image)
    input_tensor = input_tensor[tf.newaxis, ...]

    # Perform detection
    detections = model(input_tensor)

    return detections


def describe_image(image):
    # Resize the image for the model
    image_resized = image.resize((640, 480))  # Adjust size as needed
    image_np = np.array(image_resized)

    # Detect objects in the image
    detections = detect_objects(image_np)

    # Extract detection results
    detected_objects = []
    for i in range(detections['detection_boxes'].shape[1]):
        score = detections['detection_scores'][0][i].numpy()
        if score > 0.5:  # Confidence threshold
            class_id = int(detections['detection_classes'][0][i].numpy())
            detected_objects.append((class_id, score))

    return detected_objects


def take_screenshot():
    # Capture a screenshot of the entire screen
    screenshot = pyautogui.screenshot()
    cursor_position = pyautogui.position()

    # Determine the region of interest around the cursor position
    x, y = cursor_position
    region = (x - 125, y - 125, x + 125, y + 125)  # Adjusted for dynamic size
    region_image = screenshot.crop(region)

    # Use the describe_image function to classify the image
    detected_objects = describe_image(region_image)
    print(f"Detected objects: {detected_objects}")  # Print the detected objects for debugging

    # Convert the cropped image to grayscale for OCR
    region_image_gray = region_image.convert("L")
    extracted_text = pytesseract.image_to_string(region_image_gray, lang="eng+hin")

    sys.stdout.reconfigure(encoding="utf-8")
    return extracted_text, region_image


def speak_text(text):
    engine.setProperty("volume", volume)
    engine.setProperty("rate", rate)
    engine.setProperty("voice", current_voice.id)
    engine.say(text)
    engine.runAndWait()


def main_loop():
    global running
    initial_text, _ = take_screenshot()

    while running:
        if mode == 'cursor':
            # Check for cursor movement and screen change
            initial_text = detect_screen_change(initial_text)
        elif mode == 'summary':
            # Summarize the screen content
            summary = summarize_screen()
            print(summary)
            speak_text(summary)
            time.sleep(5)  # Wait before summarizing again

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


------------------------------------------------------------5th---------------
ERROR:
Detected objects: []
Detected objects: []
('', <PIL.Image.Image image mode=RGB size=250x250 at 0x1F3F3000E80>)
Detected objects: [(77, 0.5473041), (85, 0.5299681)]
('ensorflow/core/pla\nce-critical operat\ntions: AVX2 AVX512\n\ne=RGB size=250x250\n', <PIL.Image.Image image mode=RGB size=250x250 at 0x1F3F63ABF40>)
Detected objects: [(53, 0.71463513), (53, 0.6899659), (53, 0.68366593)]
('', <PIL.Image.Image image mode=RGB size=250x250 at 0x1F3F2FDFBB0>)
Detected objects: [(53, 0.75275195)]
('G Collins Dictionary\n\nAPPLE definition and mea\n', <PIL.Image.Image image mode=RGB size=250x250 at 0x1F3F63ABF40>)
Detected objects: []
('Select Mode!\n\nLaunch\n', <PIL.Image.Image image mode=RGB size=250x250 at 0x1F3F2FDFCA0>)
Detected objects: []
1.



-----------------------------------------------------object detection clarification----------------------

import wx
import threading
import pytesseract
import pyttsx3
import pyautogui
import time
import sys
import numpy as np
import tensorflow as tf
from PIL import Image, ImageStat

# Load the pre-trained model from TensorFlow
model = tf.saved_model.load("path_to_your_model_directory/saved_model")

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

# Mode selection: 'cursor' for cursor reading, 'summary' for summarization
mode = 'cursor'


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
            "7. Choose between 'Cursor Reading' and 'Summarization' modes.\n"
        )
        self.instructions_label = wx.StaticText(self.panel1, label=instructions_text)

        # Add logo and instructions label to a sizer
        instructions_sizer = wx.BoxSizer(wx.VERTICAL)
        instructions_sizer.Add(self.instructions_label, flag=wx.ALIGN_CENTER | wx.ALL, border=10)
        self.panel1.SetSizer(instructions_sizer)

        # Settings tab
        panel = self.panel2
        vbox = wx.BoxSizer(wx.VERTICAL)

        # Language selection
        language_label = wx.StaticText(panel, label="Select Language:")
        self.language_dropdown = wx.Choice(panel, choices=["English", "Hindi"])
        self.Bind(wx.EVT_CHOICE, self.on_language_select, self.language_dropdown)
        vbox.Add(language_label, flag=wx.ALIGN_CENTER | wx.ALL, border=10)
        vbox.Add(self.language_dropdown, flag=wx.EXPAND | wx.ALL, border=10)

        # Mode selection
        mode_label = wx.StaticText(panel, label="Select Mode:")
        self.mode_dropdown = wx.Choice(panel, choices=["Cursor Reading", "Summarization"])
        self.Bind(wx.EVT_CHOICE, self.on_mode_select, self.mode_dropdown)
        vbox.Add(mode_label, flag=wx.ALIGN_CENTER | wx.ALL, border=10)
        vbox.Add(self.mode_dropdown, flag=wx.EXPAND | wx.ALL, border=10)

        # Launch and Quit buttons
        button_size = wx.Size(200, 60)
        launch_button = wx.Button(panel, label="Launch", size=button_size)
        quit_button = wx.Button(panel, label="Quit", size=button_size)
        self.Bind(wx.EVT_BUTTON, self.on_launch, launch_button)
        self.Bind(wx.EVT_BUTTON, self.on_quit, quit_button)
        vbox.Add(launch_button, flag=wx.ALIGN_CENTER | wx.ALL, border=10)
        vbox.Add(quit_button, flag=wx.ALIGN_CENTER | wx.ALL, border=10)

        # Volume slider
        volume_label = wx.StaticText(panel, label="Volume:")
        self.volume_slider = wx.Slider(panel, value=int(volume * 100), minValue=0, maxValue=100, style=wx.SL_HORIZONTAL)
        self.Bind(wx.EVT_SLIDER, self.on_volume_change, self.volume_slider)
        vbox.Add(volume_label, flag=wx.ALIGN_CENTER | wx.ALL, border=10)
        vbox.Add(self.volume_slider, flag=wx.EXPAND | wx.ALL, border=10)

        # Rate slider
        rate_label = wx.StaticText(panel, label="Speech Rate:")
        self.rate_slider = wx.Slider(panel, value=rate, minValue=100, maxValue=400, style=wx.SL_HORIZONTAL)
        self.Bind(wx.EVT_SLIDER, self.on_rate_change, self.rate_slider)
        vbox.Add(rate_label, flag=wx.ALIGN_CENTER | wx.ALL, border=10)
        vbox.Add(self.rate_slider, flag=wx.EXPAND | wx.ALL, border=10)

        # Voice selection
        voice_label = wx.StaticText(panel, label="Select Voice:")
        voice_choices = [voice.name for voice in voices]
        self.voice_dropdown = wx.ComboBox(panel, choices=voice_choices, style=wx.CB_READONLY)
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

    def on_mode_select(self, event):
        global mode
        selected_mode = self.mode_dropdown.GetStringSelection()
        if selected_mode == "Cursor Reading":
            mode = 'cursor'
        elif selected_mode == "Summarization":
            mode = 'summary'


def is_image_text(image):
    # Convert the image to grayscale and calculate the average brightness
    image_gray = image.convert("L")
    stat = ImageStat.Stat(image_gray)
    brightness = stat.mean[0]

    # Heuristic: If brightness is low, it might contain text
    return brightness < 150  # Adjust threshold as needed


def detect_objects(image):
    # Convert the image to a tensor
    input_tensor = tf.convert_to_tensor(image)
    input_tensor = input_tensor[tf.newaxis, ...]

    # Perform detection
    detections = model(input_tensor)

    return detections


def describe_image(image):
    # Resize the image for the model
    image_resized = image.resize((640, 480))  # Adjust size as needed
    image_np = np.array(image_resized)

    # Detect objects in the image
    detections = detect_objects(image_np)

    # Extract detection results
    detected_objects = []
    for i in range(detections['detection_boxes'].shape[1]):
        score = detections['detection_scores'][0][i].numpy()
        if score > 0.5:  # Confidence threshold
            class_id = int(detections['detection_classes'][0][i].numpy())
            detected_objects.append((class_id, score))

    return detected_objects


def take_screenshot():
    # Capture a screenshot of the entire screen
    screenshot = pyautogui.screenshot()
    cursor_position = pyautogui.position()

    # Determine the region of interest around the cursor position
    x, y = cursor_position
    region = (x - 125, y - 125, x + 125, y + 125)  # Adjusted for dynamic size
    region_image = screenshot.crop(region)

    # Check if the image likely contains text
    if is_image_text(region_image):
        # Perform OCR
        region_image_gray = region_image.convert("L")
        extracted_text = pytesseract.image_to_string(region_image_gray, lang="eng+hin")
        print(f"Extracted text: {extracted_text}")
        return extracted_text, region_image
    else:
        # Use the describe_image function to classify the image
        detected_objects = describe_image(region_image)
        print(f"Detected objects: {detected_objects}")  # Print the detected objects for debugging
        return "", region_image


def speak_text(text):
    engine.setProperty("volume", volume)
    engine.setProperty("rate", rate)
    engine.setProperty("voice", current_voice.id)
    engine.say(text)
    engine.runAndWait()


def main_loop():
    global running
    initial_text, _ = take_screenshot()

    while running:
        if mode == 'cursor':
            # Check for cursor movement and screen change
            initial_text = detect_screen_change(initial_text)
        elif mode == 'summary':
            # Summarize the screen content
            summary = summarize_screen()
            print(summary)
            speak_text(summary)
            time.sleep(5)  # Wait before summarizing again

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





-------------------------------------------------summarization------------------------------------------------------------------------------------------------------



import wx
import threading
import pytesseract
import pyttsx3
import pyautogui
import time
import sys
import numpy as np
from PIL import Image
from gensim.summarization import summarize

# Load the pre-trained model from TensorFlow
model = tf.saved_model.load("path_to_your_model_directory/saved_model")

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

# Mode selection: 'cursor' for cursor reading, 'summary' for summarization
mode = 'cursor'


class MyFrame(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, size=(800, 600))

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
            "7. Choose between 'Cursor Reading' and 'Summarization' modes.\n"
        )
        self.instructions_label = wx.StaticText(self.panel1, label=instructions_text)

        # Add logo and instructions label to a sizer
        instructions_sizer = wx.BoxSizer(wx.VERTICAL)
        instructions_sizer.Add(self.instructions_label, flag=wx.ALIGN_CENTER | wx.ALL, border=10)
        self.panel1.SetSizer(instructions_sizer)

        # Settings tab
        panel = self.panel2
        vbox = wx.BoxSizer(wx.VERTICAL)

        # Language selection
        language_label = wx.StaticText(panel, label="Select Language:")
        self.language_dropdown = wx.Choice(panel, choices=["English", "Hindi"])
        self.Bind(wx.EVT_CHOICE, self.on_language_select, self.language_dropdown)
        vbox.Add(language_label, flag=wx.ALIGN_CENTER | wx.ALL, border=10)
        vbox.Add(self.language_dropdown, flag=wx.EXPAND | wx.ALL, border=10)

        # Mode selection
        mode_label = wx.StaticText(panel, label="Select Mode:")
        self.mode_dropdown = wx.Choice(panel, choices=["Cursor Reading", "Summarization"])
        self.Bind(wx.EVT_CHOICE, self.on_mode_select, self.mode_dropdown)
        vbox.Add(mode_label, flag=wx.ALIGN_CENTER | wx.ALL, border=10)
        vbox.Add(self.mode_dropdown, flag=wx.EXPAND | wx.ALL, border=10)

        # Launch and Quit buttons
        button_size = wx.Size(200, 60)
        launch_button = wx.Button(panel, label="Launch", size=button_size)
        quit_button = wx.Button(panel, label="Quit", size=button_size)
        self.Bind(wx.EVT_BUTTON, self.on_launch, launch_button)
        self.Bind(wx.EVT_BUTTON, self.on_quit, quit_button)
        vbox.Add(launch_button, flag=wx.ALIGN_CENTER | wx.ALL, border=10)
        vbox.Add(quit_button, flag=wx.ALIGN_CENTER | wx.ALL, border=10)

        # Volume slider
        volume_label = wx.StaticText(panel, label="Volume:")
        self.volume_slider = wx.Slider(panel, value=int(volume * 100), minValue=0, maxValue=100, style=wx.SL_HORIZONTAL)
        self.Bind(wx.EVT_SLIDER, self.on_volume_change, self.volume_slider)
        vbox.Add(volume_label, flag=wx.ALIGN_CENTER | wx.ALL, border=10)
        vbox.Add(self.volume_slider, flag=wx.EXPAND | wx.ALL, border=10)

        # Rate slider
        rate_label = wx.StaticText(panel, label="Speech Rate:")
        self.rate_slider = wx.Slider(panel, value=rate, minValue=100, maxValue=400, style=wx.SL_HORIZONTAL)
        self.Bind(wx.EVT_SLIDER, self.on_rate_change, self.rate_slider)
        vbox.Add(rate_label, flag=wx.ALIGN_CENTER | wx.ALL, border=10)
        vbox.Add(self.rate_slider, flag=wx.EXPAND | wx.ALL, border=10)

        # Voice selection
        voice_label = wx.StaticText(panel, label="Select Voice:")
        voice_choices = [voice.name for voice in voices]
        self.voice_dropdown = wx.ComboBox(panel, choices=voice_choices, style=wx.CB_READONLY)
        self.Bind(wx.EVT_COMBOBOX, self.on_voice_select, self.voice_dropdown)
        vbox.Add(voice_label, flag=wx.ALIGN_CENTER | wx.ALL, border=10)
        vbox.Add(self.voice_dropdown, flag=wx.EXPAND | wx.ALL, border=10)

        panel.SetSizer(vbox)

    def on_launch(self, event):
        self.ShowSelectionDialog()  # Show selection dialog for summarization
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

    def on_mode_select(self, event):
        global mode
        selected_mode = self.mode_dropdown.GetStringSelection()
        if selected_mode == "Cursor Reading":
            mode = 'cursor'
        elif selected_mode == "Summarization":
            mode = 'summary'

    def ShowSelectionDialog(self):
        # Create a dialog to allow the user to select the area for summarization
        dialog = wx.MessageDialog(self, "Please select the area on the screen for summarization.", "Select Area", wx.OK)
        dialog.ShowModal()
        dialog.Destroy()
        # Here you can implement the logic to allow the user to select the area using mouse events


def take_screenshot(region):
    # Capture a screenshot of the specified region
    screenshot = pyautogui.screenshot()
    region_image = screenshot.crop(region)

    # Convert the cropped image to grayscale for OCR
    region_image_gray = region_image.convert("L")
    extracted_text = pytesseract.image_to_string(region_image_gray, lang="eng+hin")

    # Print the extracted text for debugging
    print(f"Extracted text for summarization: {extracted_text}")

    # Summarize the extracted text
    if extracted_text.strip():
        try:
            summary = summarize(extracted_text, ratio=0.3)  # Summarize to 30% of the original text
            return summary
        except ValueError:
            return "Text is too short to summarize."
    else:
        return "No text found to summarize."


def summarize_screen(region):
    summary = take_screenshot(region)
    print(f"Summary: {summary}")
    return summary


def main_loop():
    global running
    while running:
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
