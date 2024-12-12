import asyncio

import tkinter as tk
from tkinter import filedialog

from bookmark2eagle import bookmark2eagle


def run_main():
    cookie_path = cookie_path_var.get()
    twi_num = twi_num_var.get()
    asyncio.run(bookmark2eagle(cookie_path, twi_num))


def select_cookie_file():
    file_path = filedialog.askopenfilename()
    cookie_path_var.set(file_path)


# Create the main window
root = tk.Tk()
root.title("Twitter Bookmark Manager")

# Cookie path entry
cookie_path_var = tk.StringVar()
cookie_path_label = tk.Label(root, text="Cookieファイルの場所:")
cookie_path_label.pack()
cookie_path_entry = tk.Entry(root, textvariable=cookie_path_var, width=50)
cookie_path_entry.pack()
cookie_path_button = tk.Button(
    root, text="Cookieファイルを選ぶ", command=select_cookie_file
)
cookie_path_button.pack()


# Default number of tweets
twi_num = 30


# Tweet number slider
twi_num_var = tk.IntVar(value=twi_num)
twi_num_label = tk.Label(root, text="チェックするBookmarkの数(レート制限注意):")
twi_num_label.pack()
twi_num_slider = tk.Scale(
    root, from_=1, to=100, orient=tk.HORIZONTAL, variable=twi_num_var
)
twi_num_slider.pack()

# Run button
run_button = tk.Button(root, text="実行", command=run_main)
run_button.pack()

# Start the GUI event loop
root.mainloop()
