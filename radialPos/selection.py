import numpy as np
from typing import List
from radialPos.constants import RadialAnalysis


def line_intersection(line1, line2):
    # Given from: https://stackoverflow.com/questions/20677795
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


class Selection(list):
    def get_center(self) -> (int, int):

        if not self:
            raise Exception("No selection found")

        min_x, max_x, min_y, max_y = np.inf, 0, np.inf, 0

        for Px, Py in self:
            if Px < min_x:
                min_x = Px
            if Px > max_x:
                max_x = Px
            if Py < min_y:
                min_y = Py
            if Py > max_y:
                max_y = Py

        cx = min_x + (max_x - min_x) / 2
        cy = min_y + (max_y - min_y) / 2

        return cx, cy

    def rearrange(self):
        angles = self.get_gammas()

        np_selection = np.array(self)
        order = np.argsort(angles)

        self.clear()

        for x, y in np_selection[order]:
            self.append((x, y))

    # Gamma-angles for each selection point (degrees)
    def get_gammas(self) -> List[float]:
        Zx = 0
        Cx, Cy = self.get_center()

        angles: List[float] = []

        for Px, Py in self:
            numerator = Cx * (Cx - Zx) - Px * (Cx + Zx)
            denominator = (Cx - Zx) * np.sqrt((Cy - Py) ** 2 + (Cx - Px) ** 2)
            gamma = np.degrees(np.arccos(numerator / denominator))

            if Py > Cy:
                gamma = 180 + (180 - gamma)

            angles.append(gamma)

        return angles

    def get_max_radius(self):
        Cx, Cy = self.get_center()
        max_radius = 0

        for Px, Py in self:
            radius = np.sqrt((Cy - Py) ** 2 + (Cx - Px) ** 2)
            if radius > max_radius:
                max_radius = radius

        return max_radius

    # Return 2 selection points between which the radius with given
    # gamma angle falls.
    def bw_selection_points(self, gamma: float):
        gammas = self.get_gammas()

        for i in range(0, len(gammas)):
            if gamma <= gammas[i]:
                P2 = self[i]
                P1 = self[i - 1]
                return P1, P2

        return self[-1], self[0]

    def get_radial_lines(self):
        Cx, Cy = self.get_center()
        max_radius = self.get_max_radius()

        extreme_points = []

        for gamma in range(0, 360, RadialAnalysis.AngleStepDegree):
            rad_gamma = np.radians(gamma)
            Rx = Cx - np.cos(rad_gamma) * max_radius
            Ry = Cy - np.sin(rad_gamma) * max_radius

            P1, P2 = self.bw_selection_points(gamma)

            # Extreme points of the radii
            Ex, Ey = line_intersection((P1, P2), ((Cx, Cy), (Rx, Ry)))
            extreme_points.append((Ex, Ey))

        return [((int(Cx), int(Cy)), (int(Px), int(Py)))
                for Px, Py in extreme_points]
