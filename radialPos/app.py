import tkinter as tk
from radialPos.model import AppModel
from radialPos.constants import AppTitle, AppModes
from radialPos.view import View


# Controller
class Application:

    def __init__(self, mode: str):
        self.root = tk.Tk()
        self.model = AppModel()
        self.view = View(self.root, self.model, mode)

    def run(self):
        self.root.title(AppTitle)
        self.root.mainloop()


app = Application(mode=AppModes.DEBUG)
app.run()
