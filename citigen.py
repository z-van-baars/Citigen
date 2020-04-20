import argparse
import pygame
import pygame.gfxdraw
import random
import string
import math
from scipy.spatial import Voronoi, Delaunay

parser = argparse.ArgumentParser()
parser.add_argument("--w",
                    default=800,
                    type=int,
                    help="This is the screen [w]idth variable")
parser.add_argument("--h",
                    default=600,
                    type=int,
                    help="This is the screen [h]eight variable")

args = parser.parse_args()


pygame.init()
pygame.display.set_mode([0, 0])

width = args.w  # default value is 800
height = args.h  # default value is 600
clock = pygame.time.Clock()
bg_blue = (16, 69, 87)
screen = pygame.display.set_mode([width, height])

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


def lloyd_relaxation(iterations, vor):
    relaxed_points = []
    for i in range(iterations):
        for region in vor.regions:
            if -1 in region or len(region) < 2:
                continue
            edges = []
            for vertex_index in region:
                if vertex_index is not -1:
                    edges.append(vor.vertices[vertex_index])
            centroid_lite = (sum(j[0] for j in edges) / len(edges),
                             sum(k[1] for k in edges) / len(edges))
            relaxed_points.append(centroid_lite)
    # there is a bug here where occasionally one point is dropped?
    # only ever one, I'm confused
    #
    # if I uncomment this next line the assertion fails about 1:6 times
    # assert len(relaxed_points) == len(vor.points)
    return relaxed_points


class Structures(object):
    def __init__(self):
        self.roads = []


class City(object):
    def __init__(self, size, walls):
        self.structures = Structures()
        self.size = size
        self.walls = walls  # 0 no walls, 1 small walls, 2 large walls
        self.points = []
        self.vor = None

    def cull_points(self):
        def is_within_borders(point):
            return (-self.size <= point[0] < self.size and
                    -self.size <= point[1] < self.size)
        interior_points = []
        for point in self.points:
            if is_within_borders(point):
                interior_points.append(point)
        self.points = interior_points

    def gen_main_roads(self):
        coordinate_range = [-100, 100]
        roads = []
        for r in range(1):
            # dict[string_id] -> [random coordinate tuple, previous sequential node
            # (default=None)]
            nodes = {}
            previous_id = None
            for n in range(5):
                node_id = generate_unique_key()
                nodes[node_id] = [generate_coordinate_pair(coordinate_range),
                                  previous_id]
                previous_id = node_id
            roads.append(nodes)
        self.structures.roads = roads

    def gen_random_pts(self):
        for i in range(int(self.size * 0.5)):
            self.points.append(generate_coordinate_pair([
                int(-self.size * 0.5),
                int(self.size * 0.5)]))

        self.vor = Voronoi(self.points)
        self.dela = Delaunay(self.points)
        print("Points: {0}, Vertices: {1}, Simplices: {2}".format(
            len(self.dela.points),
            len(self.dela.vertices),
            len(self.dela.simplices)))

    def get_edge_regions(self):
        def is_edge(simplex_pts):
            if -1 in simplex_pts:
                return True
            return False
        edge_region_indices = []
        i = 0
        for simplex in self.dela.neighbors:
            if -1 not in simplex:
                continue
            for point_index in self.dela.simplices[i]:
                edge_region_indices.append(point_index)
            i += 1
        unique_edge_regions = list(dict.fromkeys(edge_region_indices))
        edge_region_coordinates = []
        for point_index in unique_edge_regions:
            edge_region_coordinates.append(self.vor.points[point_index])

        print(len(edge_region_coordinates))
        return edge_region_coordinates


    def get_edges_programmatic(self):
        border_regions = []
        for x in range(self.size):
            distances_top = []
            distances_bottom = []
            print(len(self.points))
            for each_point in self.points:
                dist_t = get_length(each_point, (-int(self.size / 2) + x, -int(self.size / 2)))
                dist_b = get_length(each_point, (-int(self.size / 2) + x, int(self.size)))
                distances_top.append((dist_t, each_point))
                distances_bottom.append((dist_b, each_point))
            distances_top_sorted = sorted(distances_top, key=lambda d: d[1])
            distances_bottom_sorted = sorted(distances_bottom, key=lambda d: d[1])
            border_regions.append(distances_top_sorted[0][1])
            border_regions.append(distances_bottom_sorted[0][1])
        for y in range(self.size):
            distances_left = []
            distances_right = []
            for each_point in self.points:
                dist_l = get_length(each_point, (-int(self.size / 2), -int(self.size / 2) + y))
                dist_r = get_length(each_point, (int(self.size / 2), -int(self.size / 2) + y))
                distances_left.append((dist_l, each_point))
                distances_right.append((dist_r, each_point))
            distances_left_sorted = sorted(distances_left, key=lambda d: d[1])
            distances_right_sorted = sorted(distances_right, key=lambda d: d[1])
            border_regions.append(distances_left_sorted[0][1])
            border_regions.append(distances_right_sorted[0][1])
        print(len(border_regions))
        return border_regions



def generate_new(map_size, image_size):
    # Onrun junk

    # Unpack preset features if any
    #  - Coast
    #  - River
    #  - Size
    #  - Terrain

    new_city = City(map_size, 0)
    # generate random points
    new_city.gen_random_pts()
    new_city.edge_regions = new_city.get_edges_programmatic()
    # Choose Nodes for Main Roads
    # new_city.gen_main_roads()

    # Generate Polygonal Nodes for
    # Generate Major Building Nodes + Polygons for such
    #  - Castle / Fortress
    #  - Harbor / Docks
    #  - Market
    #  - Town Hall
    # High Density Block Polygons
    # Low Density Block Polygons
    # Farmland Block Polygons

    city_map_image = render_image(image_size, new_city)
    return new_city, city_map_image


def get_length(pt_A, pt_B):
    """Pythagorean Distance Formula, returns a float"""
    a2 = (pt_A[0] - pt_B[0]) ** 2
    b2 = (pt_A[1] - pt_B[1]) ** 2
    c2 = math.sqrt(a2 + b2)
    # reut
    return c2


def segment_to_polygon_pts(pt_A, pt_B, thickness, offset):
    """Returns a 4-tuple of px coordinate pairs with values offset for display"""
    angle = math.atan2(pt_A[1] - pt_B[1], pt_A[0] - pt_B[0])
    center_pt = ((pt_A[0] + pt_B[0]) / 2., (pt_A[1] + pt_B[1]) / 2.)
    length = get_length(pt_A, pt_B)
    UL = (center_pt[0] + (length / 2.) * math.cos(angle) -
          (thickness / 2.) * math.sin(angle) + offset,
          center_pt[1] + (thickness / 2.) * math.cos(angle) +
          (length / 2.) * math.sin(angle) + offset)
    UR = (center_pt[0] - (length / 2.) * math.cos(angle) -
          (thickness / 2.) * math.sin(angle) + offset,
          center_pt[1] + (thickness / 2.) * math.cos(angle) -
          (length / 2.) * math.sin(angle) + offset)
    BL = (center_pt[0] + (length / 2.) * math.cos(angle) +
          (thickness / 2.) * math.sin(angle) + offset,
          center_pt[1] - (thickness / 2.) * math.cos(angle) +
          (length / 2.) * math.sin(angle) + offset)
    BR = (center_pt[0] - (length / 2.) * math.cos(angle) +
          (thickness / 2.) * math.sin(angle) + offset,
          center_pt[1] - (thickness / 2.) * math.cos(angle) -
          (length / 2.) * math.sin(angle) + offset)
    return (UL, BL, BR, UR)


def render_image(image_size, city):
    margin = 50
    render_surface = pygame.Surface((image_size + margin * 2, image_size + margin * 2))
    render_surface.fill((10, 10, 10))
    # this moves all rendered points onto the visible surface area
    offset = int(city.size * 0.5)

    point_image = pygame.Surface((2, 2))
    point_image.fill((200, 20, 20))
    edge_point_image = pygame.Surface((2, 2))
    edge_point_image.fill((20, 230, 20))
    midpoint_image = pygame.Surface((2, 2))
    midpoint_image.fill((20, 200, 20))

    # Render Roads as adjustable pxl width polygons --------------------------------------------------------------------#

    for road in city.structures.roads:
        road_segments = []
        for node in road:
            if road[node][1] is None:
                continue
            prev_node = road[node][1]
            pt_A = road[prev_node][0]
            pt_B = road[node][0]

            road_segments.append(segment_to_polygon_pts(pt_A, pt_B, 4, offset, margin))
        for segment_points in road_segments:
            pygame.gfxdraw.aapolygon(render_surface, segment_points, (255, 255, 255))
            pygame.gfxdraw.filled_polygon(
                render_surface,
                segment_points,
                (255, 255, 255))



    # Render each voronoi region polygon in white --------------------------------------------------------------------#
    for region in city.vor.regions:
        # skip regions with fewer than 3 points or with points off the coordinate field (-1)
        if -1 in region or len(region) < 1:
            continue

        assert len(region) > 2

        # store the points from each polygon
        edge_points = []
        for vertex_index in region:
            edge_points.append(city.vor.vertices[vertex_index])
        # even_squares = [x * x for x in range(10) if x % 2 == 0]

        # apply a rendering offset half the width / height of the coordinate field
        adjusted_edge_points = []
        for edge_point in edge_points:
            adjusted_edge_points.append(
                (edge_point[0] + offset + margin,
                 edge_point[1] + offset + margin))

        # render a closed polygon for each voronoi region's points
        pygame.draw.aalines(
            render_surface,
            (255, 255, 255),
            True,
            adjusted_edge_points)
    # Render Each Delaunay Edge in Blue -------------------------------------------------------------------------------#
    i = 0
    for simplex in city.dela.simplices:
        simplex_points = []
        for point in city.vor.points[city.dela.simplices[i]]:
            simplex_points.append(point)
        adjusted_simplex_points = []
        for simplex_point in simplex_points:
            adjusted_simplex_points.append(
                (simplex_point[0] + offset + margin,
                 simplex_point[1] + offset + margin))
        pygame.draw.aalines(
            render_surface,
            (100, 100, 255),
            True,
            adjusted_simplex_points)
        i += 1
    # Render red dots for each centroid ----------------------------------------------------------------------------- #
    for point in city.points:
        render_surface.blit(point_image, [point[0] + offset + margin, point[1] + offset + margin])

    # render each border region in green ------------------------------------------------------------------------------#
    for edge_region in city.edge_regions:
        # print(edge_region)
        region_index = coordinates_to_region_index(city.vor, edge_region)
        # print("New Edge Polygon")
        adjusted_polygon_points = []
        for vertex_index in city.vor.regions[region_index]:
            # Skip any corners off the edge
            if vertex_index == -1:
                continue
            xy_pair = city.vor.vertices[vertex_index]
            # print(xy_pair)
            adjusted_polygon_points.append((
                xy_pair[0] + offset + margin,
                xy_pair[1] + offset + margin))
        # skip any polygons with fewer than 3 sides / corners
        if len(adjusted_polygon_points) < 3:
            continue

        pygame.gfxdraw.filled_polygon(
            render_surface,
            adjusted_polygon_points,
            (10, 225, 10, 110))

    # Render Each Border Point in Green
    for point in city.edge_regions:
        x = point[0] + offset + margin
        y = point[1] + offset + margin
        # assert x >= 0 and x < image_size + margin * 2
        # assert y >= 0 and y < image_size + margin * 2
        render_surface.blit(
            edge_point_image,
            [x, y])

    return render_surface


def coordinates_to_region_index(voronoi_object, coordinates):
    vor = voronoi_object
    xy1 = tuple(coordinates)
    region_index = 0
    for xyi in vor.point_region:
        xy2 = tuple(vor.points[region_index])
        if xy2[0] == xy1[0] and xy2[1] == xy1[1]:
            return xyi
        region_index += 1


def display_update(city_map_image):
    # reset and wipe screen
    screen.fill(bg_blue)

    # draw to screen
    screen.blit(city_map_image, [0, 0])
    # close out and frame limit
    pygame.display.flip()
    clock.tick(60)


new_city, city_map_image = generate_new(500, 500)
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.display.quit()
            pygame.quit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                new_points = lloyd_relaxation(2, new_city.vor)
                new_city.points = new_points
                new_city.cull_points()
                new_city.vor = Voronoi(new_city.points)
                new_city.dela = Delaunay(new_city.points)
                new_city.edge_regions = new_city.get_edges_programmatic()
                city_map_image = render_image(500, new_city)
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            mouse_pos_adj = (mouse_pos[0] - 250, mouse_pos[1] - 250)
            print(mouse_pos_adj)
    display_update(city_map_image)
