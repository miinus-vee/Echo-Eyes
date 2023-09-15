import wx
import threading
import pytesseract
import pyttsx3
import pyautogui
import time

sound = pyttsx3.init()  # tts initiated
rate = sound.getProperty("rate")  # rate determined

new_rate = rate - 50  # rate decreased by 50 units
sound.setProperty("rate", new_rate)


previous_cursor_position = pyautogui.position()
running = False


def take_screenshot():
    screenshot = pyautogui.screenshot()  # Entire Screen Screenshot
    cursor_position = pyautogui.position()

    x, y = cursor_position
    region = (x, y - 20, x + 250, y + 20)  # region determination
    region_image = screenshot.crop(region)
    region_image_gray = region_image.convert("L")
    extracted_text = pytesseract.image_to_string(region_image_gray)
    return extracted_text


def detect_screen_change(previous_text):
    global previous_cursor_position
    current_cursor_position = pyautogui.position()

    if (
        current_cursor_position != previous_cursor_position
    ):  # Check if the cursor has moved from its previous position
        new_text = take_screenshot()  # Capture a new screenshot and perform OCR

        # Compare the text extracted from the current and previous screenshots
        if new_text != previous_text:
            # If the text has changed, alert the user
            sound.stop()
            print(new_text)
            sound.say(new_text)
            sound.runAndWait()

        previous_cursor_position = current_cursor_position
        return new_text
    else:
        return previous_text


def main_loop():
    global running
    initial_text = take_screenshot()

    while running:
        initial_text = detect_screen_change(
            initial_text
        )  # Check for cursor movement and screen change
        time.sleep(1)


def start_main_loop():
    global running
    running = True
    threading.Thread(target=main_loop).start()


def stop_main_loop():
    global running
    running = False


class MyFrame(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, size=(650, 650))
        icon = wx.Icon("logo.png", wx.BITMAP_TYPE_PNG)
        self.SetIcon(icon)

        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        self.logo_bitmap = wx.Bitmap("logo.png", wx.BITMAP_TYPE_PNG)
        self.logo_staticbitmap = wx.StaticBitmap(
            panel, wx.ID_ANY, self.logo_bitmap, wx.DefaultPosition, wx.DefaultSize
        )
        vbox.Add(self.logo_staticbitmap, flag=wx.ALIGN_CENTER | wx.ALL, border=10)

        button_size = wx.Size(200, 60)  # Increase in button size
        launch_button = wx.Button(panel, label="Launch", size=button_size)
        quit_button = wx.Button(panel, label="Quit", size=button_size)
        vbox.Add(launch_button, flag=wx.ALIGN_CENTER | wx.ALL, border=10)
        vbox.Add(quit_button, flag=wx.ALIGN_CENTER | wx.ALL, border=10)

        self.Bind(wx.EVT_BUTTON, self.on_launch, launch_button)
        self.Bind(wx.EVT_BUTTON, self.on_quit, quit_button)

        panel.SetSizer(vbox)

    def on_launch(self, event):
        start_main_loop()
        self.Iconize(True)

    def on_quit(self, event):
        stop_main_loop()
        wx.CallAfter(self.Close)


app = wx.App()
frame = MyFrame(None, -1, "EchoEYES")
frame.Show()
app.MainLoop()
