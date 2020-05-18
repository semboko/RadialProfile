from typing import List, Tuple
import numpy as np
import math


class AppModel:
    FileNames: str
    CurrentImage: int = 0
    Selection = []

    def center_selection(self) -> (int, int):
        if not self.Selection:
            print("No selection found")
            return

        min_x, max_x, min_y, max_y = math.inf, 0, math.inf, 0

        for Px, Py in self.Selection:
            if Px < min_x:
                min_x = Px
            if Px > max_x:
                max_x = Px
            if Py < min_y:
                min_y = Py
            if Py > max_y:
                max_y = Py

        Cx = min_x + (max_x - min_x)/2
        Cy = min_y + (max_y - min_y)/2

        return Cx, Cy

    # Alpha-angles for each selection point
    def sp_angles(self, C: tuple):
        Zx = 0
        Cx, Cy = C

        angles = []

        for Px, Py in self.Selection:
            nom = Cx*(Cx-Zx) - Px*(Cx + Zx)
            denom = (Cx-Zx) * math.sqrt((Cy - Py)**2 + (Cx-Px)**2)
            alpha = math.degrees(math.acos(nom / denom))

            if Py > Cy:
                alpha = 180 + (180 - alpha)

            angles.append(alpha)

        return angles

    def arrange_selection(self):
        Cx, Cy = self.center_selection()
        angles = self.sp_angles((Cx, Cy))

        np_selection = np.array(self.Selection)
        order = np.argsort(angles)
        new_selection = [tuple(i) for i in np_selection[order]]
        self.Selection = new_selection

    def between_sp(self, gamma):
        Cx, Cy = self.center_selection()
        angles = self.sp_angles((Cx, Cy))

        for i in range(0, len(angles)):
            if gamma <= angles[i]:
                P2 = self.Selection[i]
                P1 = self.Selection[i-1]
                return P1, P2

        return self.Selection[-1], self.Selection[0]

    def selection_max_radius(self):
        Cx, Cy = self.center_selection()
        max_radius = 0

        for Px, Py in self.Selection:
            radius = math.sqrt((Cy-Py)**2 + (Cx-Px)**2)
            if radius > max_radius:
                max_radius = radius

        return max_radius

    @staticmethod
    def line_intersection(line1, line2):
        # From: https://stackoverflow.com/questions/20677795
        xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
        ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

        def det(a, b):
            return a[0] * b[1] - a[1] * b[0]

        div = det(xdiff, ydiff)

        if div == 0:
            raise Exception('lines do not intersect')

        d = (det(*line1), det(*line2))
        x = det(d, xdiff) / div
        y = det(d, ydiff) / div

        return x, y

    def get_radii(self):
        Cx, Cy = self.center_selection()
        max_radius = self.selection_max_radius()

        extreme_points = []

        for gamma in range(0, 360, 10):

            rad_gamma = math.radians(gamma)
            Rx = Cx - math.cos(rad_gamma) * max_radius
            Ry = Cy - math.sin(rad_gamma) * max_radius

            # Selection points intersected by the gamma-vector
            P1, P2 = self.between_sp(gamma)

            # Extreme points of the radii
            Ex, Ey = self.\
                line_intersection((P1, P2), ((Cx, Cy), (Rx, Ry)))
            extreme_points.append((Ex, Ey))

        return [((int(Cx), int(Cy)), (int(Px), int(Py)))
                for Px, Py in extreme_points]
