import sys

import numpy as np

def write_csv(file_path, csv_lines):
    if len(csv_lines) > 0:
        with open(file_path, 'w') as f:
            f.write(
                'timestamp, framestamp, label, '
                'speed, x_min, y_min, x_max, y_max, area\n'
            )
            for line in csv_lines:
                for l in line[:-1]:
                    f.write(f"{l}, ")
                f.write(f"{line[-1]}\n")
    else:
        print("No data to save, csv EMPTY")

def coords_to_points(coords):
    return [Point(ci[0], ci[1]) for ci in coords]


def isabove(line, p):
    # a, b = line
    # return (p[1] - a[1]) * (b[0] - a[0]) - (p[0] - a[0]) * (b[1] - a[1]) < 0

    line_copy = np.asarray(line).copy()
    if line_copy[0][0] > line_copy[1][0]:
        line_copy = np.asarray([line_copy[1], line_copy[0]])

    v1 = line_copy[1] - line_copy[0]
    v2 = line_copy[1] - p
    xp = v1[0] * v2[1] - v1[1] * v2[0]  # Cross product

    return xp > 0


def in_hull(point, polygon):

    goods = polygon.contains(Point(point[0], point[1]))

    return goods


class Point:
    def __init__(self, x, y):
        """
        A point specified by (x,y) coordinates in the cartesian plane
        """
        self.x = x
        self.y = y


class Polygon:
    def __init__(self, points):
        """
        points: a list of Points in clockwise order.
        """
        self.points = points
        self.P_points = coords_to_points(points)
        self.edges = self.get_edges()

    def get_edges(self):
        ''' Returns a list of tuples that each contain 2 points of an edge '''
        edge_list = []
        for i,p in enumerate(self.P_points):
            p1 = p
            p2 = self.P_points[(i+1) % len(self.P_points)]
            edge_list.append((p1,p2))

        return edge_list

    def contains(self, point):
        # _huge is used to act as infinity if we divide by 0
        _huge = sys.float_info.max
        # _eps is used to make sure points are not on the same line as vertexes
        _eps = 0.00001

        # We start on the outside of the polygon
        inside = False
        for edge in self.edges:
            # Make sure A is the lower point of the edge
            A, B = edge[0], edge[1]
            if A.y > B.y:
                A, B = B, A

            # Make sure point is not at same height as vertex
            if point.y == A.y or point.y == B.y:
                point.y += _eps

            if (point.y > B.y or point.y < A.y or point.x > max(A.x, B.x)):
                # The horizontal ray does not intersect with the edge
                continue

            if point.x < min(A.x, B.x):  # The ray intersects with the edge
                inside = not inside
                continue

            try:
                m_edge = (B.y - A.y) / (B.x - A.x)
            except ZeroDivisionError:
                m_edge = _huge

            try:
                m_point = (point.y - A.y) / (point.x - A.x)
            except ZeroDivisionError:
                m_point = _huge

            if m_point >= m_edge:
                # The ray intersects with the edge
                inside = not inside
                continue

        return inside