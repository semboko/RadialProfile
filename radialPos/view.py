import tkinter as tk
from PIL.ImageTk import PhotoImage
from PIL import Image
from tkinter.filedialog import askopenfilenames
from radialPos.model import AppModel
from radialPos.constants import AppModes
import math
from time import sleep


class LeftMenu(tk.Frame):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pack(ipadx=20)

        self.OpenFolderButton = tk.Button(self, text='Open Folder...')
        self.OpenFolderButton.pack()

        self.NextImageButton = tk.Button(self, text='Next Image >>')
        self.NextImageButton.pack()

        self.ClearSelectionButton = tk.Button(self, text='Clear Selection')
        self.ClearSelectionButton.pack()

        self.CalculateButton = tk.Button(self, text='Calculate RP')
        self.CalculateButton.pack()


class View:
    def __init__(self, root: tk.Tk, model: AppModel, mode: str):
        self.root = root
        self.frame = tk.Frame(self.root)
        self.frame.grid(row=0, column=0)
        self.model = model
        self.mode = mode

        self.left_menu = LeftMenu(self.frame)
        self.left_menu.grid(row=0, column=0)

        self.left_menu.OpenFolderButton.bind(
            '<Button-1>', self.open_filedialog)

        self.left_menu.NextImageButton.bind(
            '<Button-1>', self.next_image)

        self.left_menu.ClearSelectionButton.bind(
            '<Button-1>', self.clear_selection)

        self.left_menu.CalculateButton.bind(
            '<Button-1>', self.calculate_rp)

        self.canvas = tk.Canvas(width=root.winfo_screenwidth() - 500,
                                height=root.winfo_screenheight() - 300)
        self.canvas.grid(row=0, column=1)

        self.canvas.bind('<Button-1>', self.selection_click)

    def open_filedialog(self, event):
        self.root.update()
        self.model.FileNames = askopenfilenames(
            initialdir='~/Pictures', filetypes=[("Images", ".png .jpg .tiff")])

        print(f'Chosen: {self.model.FileNames}')

        self.update_canvas()

    def next_image(self, event):
        self.model.CurrentImage = \
            (self.model.CurrentImage + 1) % len(self.model.FileNames)

        print(f'CurrentImage: {self.model.FileNames[self.model.CurrentImage]}')

        self.clear_selection(event)
        self.update_canvas()

    def update_canvas(self):
        self.canvas.delete('all')
        self.root.img = img = PhotoImage(file=self.model.FileNames[self.model.CurrentImage])
        self.canvas.create_image(img.width()/2, img.height()/2, image=img)

    def selection_click(self, event):
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        self.model.Selection.append((x, y))
        self.draw_current_selection()

    def clear_selection(self, event):
        self.model.Selection.clear()
        self.update_canvas()

    def draw_current_selection(self):
        self.canvas.delete('selection')

        if len(self.model.Selection) > 2:
            self.model.arrange_selection()

        for x, y in self.model.Selection:
            self.canvas.create_oval(x-5, y-5, x+5, y+5,
                                    fill='red', tags='selection')
            # self.canvas.create_text(x, y, text=f'({x}, {y})')

        if len(self.model.Selection) < 2:
            return

        self.canvas.create_line(
            self.model.Selection, self.model.Selection[0],
            fill='red', dash=True, tags='selection')

    def calculate_rp(self, event):
        Cx, Cy = self.model.center_selection()
        self.canvas.create_oval(Cx-5, Cy-5, Cx+5, Cy+5, fill='green')
        radii = self.model.get_radii()

        for radius in radii:
            self.canvas.create_line(*radius, fill='green', dash=True)

        img = Image.open(self.model.FileNames[self.model.CurrentImage])
        pixels = img.load()
        print(pixels[Cy, Cy])