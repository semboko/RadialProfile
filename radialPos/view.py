import tkinter as tk
from PIL.ImageTk import PhotoImage
from PIL import Image
from tkinter.filedialog import askopenfilenames
from radialPos.model import AppModel
from radialPos.constants import RadialAnalysis
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
            self.model.arrange_selection()

        for x, y in self.model.Selection:
            self.canvas.create_oval(x-5, y-5, x+5, y+5,
                                    fill='red', tags='selection')

        if len(self.model.Selection) < 2:
            return

        self.canvas.create_line(
            self.model.Selection, self.model.Selection[0],
            fill='red', dash=True, tags='selection')

    def _local_intensity(self, pixels, X, Y):
        local_intensities = []
        for i in range(X - 5, X + 5):
            for j in range(Y - 5, Y + 5):
                local_intensities.append(pixels[i, j])

        self.canvas.create_rectangle(
            X - 5, Y - 5, X + 5, Y + 5, fill='green')

        return sum(local_intensities)/25

    def calculate_rp(self, event):

        radii = self.model.get_radii()

        for radius in radii:
            self.canvas.create_line(*radius, fill='green', dash=True)

        img = Image\
            .open(self.model.FileNames[self.model.CurrentImage])\
            .convert("L")
        pixels = img.load()

        gammas = range(0, 360, RadialAnalysis.AngleStepDegree)
        radial_positions = \
            [i for i in range(0, 100 + RadialAnalysis.RPStepPercent,
                              RadialAnalysis.RPStepPercent)]

        rp_data = []

        for radius, gamma in zip(radii, gammas):
            Rx, Ry = radius[1]
            Cx, Cy = radius[0]

            d = np.sqrt((Rx - Cx)**2 + (Ry - Cy)**2)

            radius_intensities = []
            for radial_pos in radial_positions:

                d_pos = d * radial_pos / 100
                delta_x = int(np.cos(np.radians(gamma)) * d_pos)
                delta_y = int(np.sin(np.radians(gamma)) * d_pos)

                PosX = Cx - delta_x
                PosY = Cy - delta_y

                local_intensity = self._local_intensity(pixels, PosX, PosY)
                radius_intensities.append(local_intensity)

            rp_data.append(radius_intensities)

        radial_intensity = np.sum(np.array(rp_data), axis=0)

        fig, ax = plt.subplots()
        ax.plot(radial_positions, radial_intensity)
        plt.show()
