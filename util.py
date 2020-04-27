import random
import math
import string


CHARACTERS = (string.ascii_letters +
              string.digits +
              '-._~')


def generate_unique_key(length=8):
    """Returns a unique unicode key of length l, default=8"""
    return ''.join(random.sample(CHARACTERS, length))

def generate_coordinate_pair(minmax):
    x = random.randrange(minmax[0], minmax[1])
    y = random.randrange(minmax[0], minmax[1])
    return (x, y)


def get_midpoint(a, b):
    x1 = (a[0] - b[0]) / 2.
    y1 = (a[1] - b[1]) / 2.
    return x1, y1


def coordinates_to_region_index(voronoi_object, coordinates):
    vor = voronoi_object
    xy1 = tuple(coordinates)
    region_index = 0
    for xyi in vor.point_region:
        xy2 = tuple(vor.points[region_index])
        if xy2[0] == xy1[0] and xy2[1] == xy1[1]:
            return xyi
        region_index += 1
    print("no match found")


def coordinates_to_point_index(voronoi_object, coordinates):
    vor = voronoi_object
    xy1 = tuple(coordinates)
    for point_index, point in enumerate(vor.points):
        xy2 = tuple(point)
        if xy2[0] == xy1[0] and xy2[1] == xy1[1]:
            return point_index


def coord_list_match(list1, point1):
    for point_2 in list1:
        if point1[0] == point2[0] and point1[1] == point2[1]:
            return True
    return False


def get_closest_edge(map_size, point):
    distances = [(get_length(point, (point[0], -map_size * 0.5)), 0),
                 (get_length(point, (point[0], map_size * 0.5)), 1),
                 (get_length(point, (-map_size * 0.5, point[1])), 2),
                 (get_length(point, (map_size * 0.5, point[1])), 3)]
    return sorted(distances, key=lambda d: d[0])[0][1]


def get_neighbors(dela, vertex):
    # unpack vertex_neighbor_vertices just so it's easier to type
    a = dela.vertex_neighbor_vertices[0]
    b = dela.vertex_neighbor_vertices[1]
    # The indices of neighboring vertices of 'vertex' are indptr[indices['vertex']:indices['vertex'+1]].
    return b[a[vertex] : a[vertex + 1]]



def get_length(pt_A, pt_B):
    """Pythagorean Distance Formula, returns a float"""
    a2 = (pt_A[0] - pt_B[0]) ** 2
    b2 = (pt_A[1] - pt_B[1]) ** 2
    c2 = math.sqrt(a2 + b2)
    # reut
    return c2


def lloyd_relaxation(vor):
    """A Pseudo-Lloyd relaxation function that just averages the points of resulting voronoi
    polygons together and returns an approximated centroid.  This will nicely spread out bunched
    up dots, but it does have a tendency over time to spread points out, with a disproportionate
    effect on points toward the edges of the graph.

    A potential idea for future improvement is to have some kind of diff function that would compensate
    for points drifting off the edge.  Right now there's a cull function that takes place immediately
    after this function is called that trims off any points that crept out of the scope of the graph.
    This works and is fast but it does ultimately result in a reduction of the number of dots overall."""
    relaxed_points = []
    for r_index, region in enumerate(vor.regions):
        corners = []
        for vertex_index in region:
            if vertex_index is not -1:
                corners.append(vor.vertices[vertex_index])

        # don't change any region centroids with vertices outside the voronoi
        if -1 in region:
            relaxed_points.append(vor.points[r_index - 1])
            continue

        # skip the dummy empty region
        if len(region) < 3:
            continue

        centroid_lite = (int(sum(j[0] for j in corners) / len(corners)),
                         int(sum(k[1] for k in corners) / len(corners)))
        relaxed_points.append(centroid_lite)
    # there is a bug here where occasionally one point is dropped?
    # only ever one, I'm confused
    #
    # if I uncomment this next line the assertion fails about 1:6 times
    # assert len(relaxed_points) == len(vor.points)
    return relaxed_points

