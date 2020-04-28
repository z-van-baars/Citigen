import argparse
import pygame
import random
import render as rdr
from input import input_handler
from city import City


parser = argparse.ArgumentParser()
parser.add_argument("--w",
                    default=1200,
                    type=int,
                    help="This is the screen [w]idth variable")
parser.add_argument("--h",
                    default=650,
                    type=int,
                    help="This is the screen [h]eight variable")

args = parser.parse_args()
pygame.init()
pygame.display.set_mode([args.w, args.h])
width = args.w  # default value is 1000
height = args.h  # default value is 600


class GenerationParameters(object):
    def __init__(self, city):
        self.n_majroads = random.randint(
            min(max(1, int(city.size / 2)), 2),
            min(int(city.size * 3), 10))
        nmr = city.size * 2 * city.map_size / 150
        self.n_minroads = random.randint(int(nmr / 3), int(nmr))
        self.n_minroads = 100
        nfr = city.size ** 2 * city.map_size / 100
        self.n_fillroads = random.randint(int(nfr / 3), int(nfr))
        self.n_fillroads = 0
        # max 100 -> % chance of taking an inefficient step on node creation
        self.road_curviness = 50
        self.river_curviness = 75
        self.inner_radius = city.map_size * 0.03 * city.size
        self.outer_radius = city.map_size * 0.05 * city.size


class State(object):
    def __init__(self, screen_dimensions, map_size, city_size, image_size):
        self.screen = pygame.display.set_mode(
            [screen_dimensions[0],
             screen_dimensions[1]])
        self.clock = pygame.time.Clock()
        self.city = City(map_size, city_size, 0)
        self.gen_parameters = GenerationParameters(self.city)
        self.render_parameters = rdr.RenderParameters(
            screen_dimensions,
            map_size,
            image_size)
        self.screen_width = screen_dimensions[0]
        self.screen_height = screen_dimensions[1]
        self.city_map_image = pygame.Surface([image_size, image_size])
        self.mouse_down = False
        self.drag_start = ()


def generate_new(screen_dimensions, map_size, size, image_size):
    # Onrun junk
    state = State(screen_dimensions, map_size, size, image_size)

    wait_screen = rdr.render_wait_screen(state.render_parameters)
    rdr.display_update(
        state,
        state.screen,
        wait_screen,
        [state.screen_width, state.screen_height],
        state.render_parameters.scroll_x,
        state.render_parameters.scroll_y)

    # Unpack preset features if any
    #  - Coast
    #  - River
    #  - Size
    #  - Terrain
    # generate random points
    state.city.gen_random_pts()
    state.city.get_edge_regions()

    state.city.relax_points()
    state.city.generate_structures(state.gen_parameters)
    # Choose Nodes for Main Roads
    # state.city.gen_main_roads()

    # a = state.city.dela.vertex_neighbor_vertices[0]
    # b = state.city.dela.vertex_neighbor_vertices[1]
    # for i in state.city.points:
    #     print(b[a[i]:a[i+1]])
    # print(state.city.dela.vertex_neighbor_vertices)

    # Generate Polygonal Nodes for
    # Generate Major Building Nodes + Polygons for such
    #  - Castle / Fortress
    #  - Harbor / Docks
    #  - Market
    #  - Town Hall
    # High Density Block Polygons
    # Low Density Block Polygons
    # Farmland Block Polygons

    state.city_map_image = rdr.render_image(
        state.city,
        state.render_parameters)
    return state


# start settings
state = generate_new(
    [width, height],  # screen dimensions
    height - 20,  # map size in "tiles"
    4,  # city size [1: village, 2: town, 3: city, 4: metro]
    height - 20)  # image size in pixels


while True:
    input_handler(state)
    if state.mouse_down:
        pos = pygame.mouse.get_pos()
        pos_adj = (pos[0] - state.drag_start[0], pos[1] - state.drag_start[1])
        state.render_parameters.scroll_x = pos_adj[0]
        state.render_parameters.scroll_y = pos_adj[1]

    rdr.display_update(
        state,
        state.screen,
        state.city_map_image,
        [state.screen_width, state.screen_height],
        state.render_parameters.scroll_x,
        state.render_parameters.scroll_y)
