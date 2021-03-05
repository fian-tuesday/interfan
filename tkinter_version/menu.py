import tkinter as tk
from PIL import Image
#from interfan_model import InterferogramModel


#class MainWindow(tk.Tk):
#    def init_menu(self):
#        menu_bar = tk.Menu(self)  # menu begins


app = tk.Tk()
app.title("Interfan app")
mainmenu = tk.Menu(app) 
app.config(menu=mainmenu) 
filemenu = tk.Menu(mainmenu, tearoff=0)
filemenu.add_command(label="Открыть...")
filemenu.add_command(label="Новый")
filemenu.add_command(label="Сохранить...")
filemenu.add_command(label="Выход")
 
helpmenu = tk.Menu(mainmenu, tearoff=0)
helpmenu.add_command(label="Помощь")
helpmenu.add_command(label="О программе")
 
mainmenu.add_cascade(label="Файл", menu=filemenu)
mainmenu.add_cascade(label="Справка", menu=helpmenu)

app.geometry('300x200')
statusbar = tk.Label(app, text="Status bar with non-changing text", bd=1, relief=tk.SUNKEN, anchor=tk.W)
statusbar.pack(side=tk.BOTTOM, fill=tk.X)

#l1 = Label(width=7, height=4, bg='yellow', text="1")
#l2 = Label(width=7, height=4, bg='orange', text="2")
#l3 = Label(width=7, height=4, bg='lightgreen', text="3")
#l4 = Label(width=7, height=4, bg='lightblue', text="4")

#l1.pack()
#l2.pack()
#l3.pack()
#l4.pack()
app.mainloop()

#im = Image.open('a_image.tif')
#im.show()

