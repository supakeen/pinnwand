import pyperclip as pc


def verify_clipboard_contents(value):
    assert pc.paste() == value, "Clipboard had incorrect content"
