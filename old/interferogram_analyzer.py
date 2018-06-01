import tkinter as tk
import tkinter.filedialog as filedialog
import PIL.Image
import PIL.ImageTk
import math

"""
import numpy as np
import matplotlib.pyplot as plt
import collections
"""

possible_file_types = (("TIFF files", "*.tif *.tiff"), ("all files", "*.*"))


class MainWindow(tk.Tk):
    buttons_width = 20

    def __init__(self):
        super().__init__()
        self._interferogram_image_filename = ""
        self._create_frames()

    def _create_frames(self):
        self.dashboard = tk.Frame(self)
        self.dashboard.grid(row=0, sticky="nw")
        self.image_holder = InterferogramView(self)
        self.image_holder.grid(row=1, sticky="nesw")
        self.status = StatusBar(self)
        self.status.grid(row=2, sticky="sew")

        self.button_load_image = tk.Button(self.dashboard, width=MainWindow.buttons_width,
                                           text="Load image", command=self.load_image_dialog)
        self.button_load_image.grid(row=0, column=0)
        self.button_find_base_points = tk.Button(self.dashboard, width=MainWindow.buttons_width,
                                                 text="Find base points", command=self._find_base_points)
        self.button_find_base_points.grid(row=0, column=2)
        self.button_save_image = tk.Button(self.dashboard, width=MainWindow.buttons_width,
                                           text="Save image", command=self.save_image_dialog)
        self.button_save_image.grid(row=0, column=1)

    def _find_base_points(self):
        # if not self._left_frame._interferogram_image_filename:
        #    print("Should open interferogram image first!")
        #    return
        self.status.set("Поиск базовых точек пока не реализован (TODO)")

    def load_image_dialog(self):
        self.status.set("Select image file to load...")
        filename = tk.filedialog.askopenfilename(initialdir="/", title="Select interferogram image file",
                                                 filetypes=possible_file_types)
        if not filename:
            self.status.clear()
        else:
            self._interferogram_image_filename = filename
            self.status.set("Loading image file {0}...", filename)
            self.image_holder.load_image(filename)
            self.status.set("Loaded image file {0} successfully.", filename)

    def save_image_dialog(self):
        self.status.set("Select image file to save...")
        filename = tk.filedialog.asksaveasfilename(initialdir="/", title="Select file",
                                                   filetypes=possible_file_types)
        if not filename:
            self.status.clear()
        else:
            self.status.set("Saving image as {0}", filename)
            self.image_holder.save_image(filename)
            self._interferogram_image_filename = filename
            self.status.set("Saved image file {0} successfully.", filename)


class StatusBar(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self._label = tk.Label(master, text="", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self._label.grid(sticky="nesw")

    def set(self, format_string, *args):
        self._label.config(text=format_string.format(*args))
        self._label.update_idletasks()

    def clear(self):
        self._label.config(text="")
        self._label.update_idletasks()


# === Отображение ===
class ResizableCanvasView(tk.Frame):
    """ Поддерживает масштабируемый холст, на котором будут отображаться:
        - интерферограмма,
        - базовые точки для выделения интерференционных линий,
        - интерференционные линии.
        Учитывает приближение и смещение.
    """
    initial_canvas_width = 600
    initial_canvas_height = 600

    def __init__(self, master):
        super().__init__(master)
        self.canvas = tk.Canvas(self, width=self.initial_canvas_width, height=self.initial_canvas_height)
        self.canvas.grid(row=0, column=0, sticky="nesw")
        self.control = ResizableCanvasControl(self)

        self.bind("<Configure>", self.on_resize)
        self.height = self.winfo_reqheight()
        self.width = self.winfo_reqwidth()

    def on_resize(self, event):
        # determine the ratio of old width/height to new width/height
        wscale = float(event.width)/self.width
        hscale = float(event.height)/self.height
        self.width = event.width
        self.height = event.height
        # resize the canvas
        self.config(width=self.width, height=self.height)
        # rescale all the objects tagged with the "all" tag
        self.scale("all", 0, 0, wscale, hscale)


class InterferogramView:
    """ Поддерживает отображение на холсте интерферограммы """

    def __init__(self, master):
        self.canvas.create_line(0, 0, self.initial_canvas_width-1, self.initial_canvas_height-1)
        self.canvas.create_line(0, self.initial_canvas_height-1, self.initial_canvas_width-1, 0)
        self.pil_image = None
        self.image_tk = None
        self.image_id_on_canvas = None

    def load_image(self, filename):
        self.pil_image = PIL.Image.open(filename)
        self.canvas.config(width=self.pil_image.width, height=self.pil_image.height)
        self.image_tk = PIL.ImageTk.PhotoImage(self.pil_image)
        self.image_id_on_canvas = self.canvas.create_image(self.image_tk.width() // 2, self.image_tk.height() // 2,
                                                           image=self.image_tk)
        # print(self.image_tk.width(), self.image_tk.height())

    def resize_image(self, factor):
        self.pil_image = self.pil_image.resize((self.pil_image.width*2, self.pil_image.height*2),
                                               resample=PIL.Image.NEAREST)
        self.image_tk = PIL.ImageTk.PhotoImage(self.pil_image)
        self.image_id_on_canvas = self.canvas.create_image(self.image_tk.width() // 2, self.image_tk.height() // 2,
                                                           image=self.image_tk)


def main():
    main_window = MainWindow()
    main_window.mainloop()


if __name__ == '__main__':
    main()
