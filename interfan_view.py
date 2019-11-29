import tkinter as tk
import tkinter.filedialog as filedialog
import PIL.Image
import PIL.ImageTk

import interfan_control as control
import interfan_model as model
from configurations import *
from observer import Observer
from PIL import Image, ImageTk

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.menu = self.init_menu()
        path = 'interferogram.tif'
        model.InterferogramModel.set_image(self, 'interferogram.tif')
        img = model.InterferogramModel.open_image(self)
        interferogram = tk.Label(self, image=img)
        interferogram.pack(side="left")

        #model.InterferogramModel.set_image(self, path)
        #img = model.InterferogramModel.open_image('interferogram.tif')


        #img = model.InterferogramModel.prepared_image(self)
        #img1 = ImageTk.PhotoImage(model.InterferogramModel.open_image(self))

        #interferogram.pack(side="left")
        #interferogram1 = tk.Label(self, image=img)
        #interferogram1.pack(side="right")
       # self.toolbar = tk.Frame(self)
       # self.buttons = self.init_toolbar_buttons()
       # self.analyzer = self.init_analyzer()
       # self.status = self.init_status()
       # self.toolbar.grid(row=0, sticky="nw")
       # self.analyzer.grid(row=1, sticky="nsew")
       # self.status.grid(row=2, sticky="sew")

       # self.bind_controllers()

    def init_menu(self):
        menu_bar = tk.Menu(self)  # menu begins

        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label='New analysis', accelerator='Ctrl+N', compound='left', underline=0)
        file_menu.add_command(label='Open analysis', accelerator='Ctrl+O', compound='left', underline=0)
        file_menu.add_command(label='Save analysis', accelerator='Ctrl+S', compound='left', underline=0)
        file_menu.add_separator()
        file_menu.add_command(label='Exit', accelerator='Alt+F4')
        menu_bar.add_cascade(label='File', menu=file_menu)

        view_menu = tk.Menu(menu_bar, tearoff=0)
        view_menu.add_command(label='Show base points', accelerator='.', compound='left', underline=0)
        view_menu.add_command(label='Show lines', accelerator='/', compound='left', underline=0)
        menu_bar.add_cascade(label='View', menu=view_menu)

        analyzer_menu = tk.Menu(menu_bar, tearoff=0)
        view_menu.add_command(label='Detect base points', accelerator='Ctrl+.', compound='left', underline=0)
        view_menu.add_command(label='Trace interference lines', accelerator='Ctrl+/', compound='left', underline=0)
        menu_bar.add_cascade(label='Analysis', menu=analyzer_menu)

        about_menu = tk.Menu(menu_bar, tearoff=0)
        about_menu.add_command(label='Help', accelerator='F1')
        about_menu.add_command(label='About')
        menu_bar.add_cascade(label='About', menu=analyzer_menu)

        self.config(menu=menu_bar)
        return menu_bar

    def init_analyzer(self):
        analyzer = AnalyzerView(self)
        return analyzer

    def init_status(self):
        status = StatusBar(self)
        return status

    def init_toolbar_buttons(self):
        buttons = {}
        for i, button_name, button_text in [(0, "load_interferogram", "Load TIFF"),
                                            (1, "find_base_points", "Points"),
                                            (2, "trace_lines", "Trace"),
                                            (3, "calc_phases", "Phases"),
                                            (4, "save_phases", "Save phases")]:
            buttons[button_name] = tk.Button(self.toolbar, width=BUTTON_DEFAULT_WIDTH, text=button_text)
            buttons[button_name].grid(row=0, column=i)
        return buttons

    def bind_controllers(self):
        """ Привязывает события нажатий кнопок к методам контроллеров. """
        self.buttons["load_interferogram"]["command"] = self.load_interferogram_dialog
        self.buttons["save_phases"]["command"] = self.save_phases_dialog

    def load_interferogram_dialog(self):
        self.status.set("Select image file to load...")
        filename = tk.filedialog.askopenfilename(initialdir="/", title="Select interferogram image file",
                                                 filetypes=POSSIBLE_FILE_TYPES)
        if not filename:
            self.status.clear()
        else:
            self.status.set("Loading image file {0}...", filename)
            self.analyzer.control.load_interferogram(filename)
            self.status.set("Loaded image file {0} successfully.", filename)

    def save_phases_dialog(self):
        self.status.set("Select image file to save...")
        filename = tk.filedialog.asksaveasfilename(initialdir="/", title="Select file",
                                                   filetypes=POSSIBLE_FILE_TYPES)
        if not filename:
            self.status.clear()
        else:
            self.status.set("Saving image as {0}", filename)
            self.analyzer.control.save_phases(filename)
            self.status.set("Saved image file {0} successfully.", filename)


class AnalyzerView(tk.Frame):
    """ Поддерживает холст, на котором будут отображаться:
        - интерферограмма,
        - базовые точки для выделения интерференционных линий,
        - интерференционные линии.
        - фазовая картинка
        Планы: в будущем даст возможность приблизиться к части интерферограммы и перемещаться по ней в х2 масштабе.
    """
    def __init__(self, master):
        super().__init__(master)
        self.model = model.AnalyzerModel()
        self.control = control.AnalyzerControl(self.model)

        self.canvas = self._create_canvas()
        self.interferogram = InterferogramView(self.canvas)
        self.base_points = BasePointsView(self.canvas)
        self.lines = LinesView(self.canvas)
        self.phases = PhasesView(self.canvas)

    def _create_canvas(self):
        canvas = tk.Canvas(self, width=INITIAL_CANVAS_WIDTH, height=INITIAL_CANVAS_HEIGHT)
        canvas.grid(row=0, column=0, sticky="nesw")
        return canvas


class InterferogramView(Observer):
    """ Поддерживает отображение на холсте интерферограммы """
    def __init__(self, canvas):
        self.model = model.InterferogramModel()
        self.control = control.InterferogramControl(self.model)

        self.canvas = canvas
        self.canvas.create_line(0, 0, INITIAL_CANVAS_WIDTH - 1, INITIAL_CANVAS_HEIGHT - 1)
        self.canvas.create_line(0, INITIAL_CANVAS_HEIGHT - 1, INITIAL_CANVAS_WIDTH - 1, 0)

    def update(self, message):
        print(message)


class BasePointsView(Observer):
    """ Поддерживает на холсте изображения базовых точек. """
    def __init__(self, canvas):
        self.model = model.BasePointsModel()
        self.control = control.BasePointsControl(self.model)

        self.canvas = canvas

    def update(self, message):
        print(message)


class LinesView(Observer):
    """ Поддерживает на холсте изображения базовых точек. """

    def __init__(self, canvas):
        self.model = model.LinesModel()
        self.control = control.LinesControl(self.model)

        self.canvas = canvas

    def update(self, message):
        print(message)


class PhasesView(Observer):
    """ Поддерживает на холсте изображение фазовой картинки. """
    def __init__(self, canvas):
        self.model = model.PhasesModel()
        self.control = None  # Данный виджет является неуправляемым

        self.canvas = canvas

    def update(self, message):
        print(message)


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
