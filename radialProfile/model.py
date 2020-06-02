from radialProfile.selection import Selection
from PIL import Image
from radialProfile.constants import RadialAnalysis
import numpy as np


class AppModel:
    FileNames: str
    CurrentImage: int = 0
    Selection: Selection = Selection()

    def increment_current_image(self):
        self.CurrentImage = (self.CurrentImage + 1) % len(self.FileNames)
        print(f'CurrentImage: {self.FileNames[self.CurrentImage]}')

    def decrement_current_image(self):
        self.CurrentImage = (self.CurrentImage - 1) % len(self.FileNames)
        print(f'CurrentImage: {self.FileNames[self.CurrentImage]}')

    @staticmethod
    def _local_intensity(pixels, X, Y):
        local_intensities = []
        for i in range(X - 5, X + 5):
            for j in range(Y - 5, Y + 5):
                local_intensities.append(pixels[i, j])

        # self.canvas.create_rectangle(
        #     X - 5, Y - 5, X + 5, Y + 5, fill='green')

        return sum(local_intensities)/25

    def scan_current_selection(self):
        radial_lines = self.Selection.get_radial_lines()

        img = Image \
            .open(self.FileNames[self.CurrentImage]) \
            .convert("L")

        pixels = img.load()

        radial_steps = range(0, 360, RadialAnalysis.AngleStepDegree)

        radial_positions = \
            [i for i in range(0, 100 + RadialAnalysis.RPStepPercent,
                              RadialAnalysis.RPStepPercent)]

        rp_data = []

        for radial_line, gamma in zip(radial_lines, radial_steps):
            Rx, Ry = radial_line[1]
            Cx, Cy = radial_line[0]

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

        radial_intensities = np.sum(np.array(rp_data), axis=0)

        return radial_positions, radial_intensities

