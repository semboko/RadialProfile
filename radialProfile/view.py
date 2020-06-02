import tkinter as tk
from PIL.ImageTk import PhotoImage
from tkinter.filedialog import askopenfilenames
from radialProfile.model import AppModel
from radialProfile.constants import RadialAnalysis
import numpy as np
import matplotlib.pyplot as plt


class LeftMenu(tk.Frame):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pack(ipadx=20)

        im = tk.PhotoImage(file='./icons/OPEN_button.png')
        self.OpenFolderButton = tk.Button(self, text='  Open Folder...  ',
                                          image=im, compound=tk.LEFT,
                                          cursor="hand2")
        self.OpenFolderButton.image = im
        self.OpenFolderButton.pack(side=tk.TOP, ipadx=5, ipady=10)

        im = tk.PhotoImage(file='./icons/NI_button.png')
        self.NextImageButton = tk.Button(self, text='  Next Image      ',
                                         image=im, compound=tk.LEFT,
                                         cursor="hand2")
        self.NextImageButton.image = im
        self.NextImageButton.pack(side=tk.TOP, ipadx=5, ipady=10)

        im = tk.PhotoImage(file='./icons/CS_button.png')
        self.ClearSelectionButton = tk.Button(self, text='  Clear Selection',
                                              image=im, compound=tk.LEFT,
                                              cursor="hand2")
        self.ClearSelectionButton.image = im
        self.ClearSelectionButton.pack(side=tk.TOP, ipadx=5, ipady=10)

        im = tk.PhotoImage(file='./icons/RP__button.png')
        self.CalculateButton = tk.Button(self, text='  Calculate RP    ',
                                         image=im, compound=tk.LEFT,
                                         cursor="hand2")
        self.CalculateButton.image = im
        self.CalculateButton.pack(side=tk.TOP, ipadx=5, ipady=10)


class View:
    def __init__(self, root: tk.Tk, model: AppModel, mode: str):
        self.root = root
        self.frame = tk.Frame(self.root)
        self.frame.grid(row=0, column=0, sticky=tk.N)
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

        self.canvas = tk.Canvas(cursor='cross', bg='pink')
        self.canvas.grid(row=0, column=1, sticky=tk.W)
        self.canvas.bind('<Button-1>', self.selection_click)

    def open_filedialog(self, event):
        self.root.update()
        self.model.FileNames = askopenfilenames(
            initialdir='~/Pictures', filetypes=[("Images", ".png .jpg .tiff")])

        if not self.model.FileNames:
            return

        print(f'Chosen: {self.model.FileNames}')

        self.update_canvas()

    def next_image(self, event):
        self.model.increment_current_image()
        self.update_canvas()

    def update_canvas(self):
        self.canvas.delete('all')

        if len(self.model.FileNames) == 0:
            return

        self.root.img = img = \
            PhotoImage(file=self.model.FileNames[self.model.CurrentImage])

        self.canvas.config(width=img.width(), height=img.height())

        self.canvas.create_image(img.width()/2, img.height()/2, image=img,
                                 tags=['image'])

        self.root.winfo_toplevel().title(
            self.model.FileNames[self.model.CurrentImage])

        self.draw_current_selection()

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
            self.model.Selection.rearrange()

        for x, y in self.model.Selection:
            self.canvas.create_oval(x-5, y-5, x+5, y+5,
                                    fill='red', tags='selection')

        if len(self.model.Selection) < 2:
            return

        self.canvas.create_line(
            self.model.Selection, self.model.Selection[0],
            fill='red', dash=True, tags='selection')

    def calculate_rp(self, event):

        # Draw radii
        radii = self.model.Selection.get_radial_lines()
        for radius in radii:
            self.canvas.create_line(*radius, fill='green', dash=True)

        radial_positions, radial_intensity = \
            self.model.scan_current_selection()

        self.show_plot(radial_positions, radial_intensity)

    def show_plot(self, radial_positions, radial_intensity):
        fig, ax = plt.subplots()
        ax.plot(radial_positions, radial_intensity)
        ax.set_xticks([0, 25, 50, 75, 100])
        ax.set_xticklabels(['Center', 25, 50, 75, 'Envelope'])
        plt.show()
