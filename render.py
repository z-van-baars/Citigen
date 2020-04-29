import pygame
import util
import math
import random
import pygame.gfxdraw


pygame.init()
pygame.display.set_mode([0, 0])
pygame.display.set_caption("Citigen v 0.1")
citigen_icon = pygame.image.load("art/citigen.png")
pygame.display.set_icon(citigen_icon)


class Colors(object):
    bg_blue = (16, 69, 87)
    background = (
        (240, 210, 175),  # normal display
        (20, 20, 20))  # mesh mode / dark mode
    points = (
        (200, 20, 20),
        (200, 20, 20))
    region_borders = (
        (20, 20, 20),
        (255, 255, 255))
    edge_points = (
        (20, 230, 20),
        (20, 230, 20))
    delaunay_edges = (
        (100, 100, 255),
        (100, 100, 255))
    low_density = (
        (68, 81, 245, 100),
        (68, 81, 245, 100))
    high_density = (
        (210, 8, 105, 125),
        (204, 8, 105, 100))
    plaza = (
        (200, 200, 100),
        (200, 200, 100))
    plaza_fill = (
        (255, 225, 255, 100),
        (255, 225, 255, 100))
    edge_region_fill = (
        (10, 225, 10, 110),
        (10, 225, 10, 110))
    major_road = (
        (20, 20, 20),
        (255, 255, 255))
    minor_road = (
        (50, 50, 50),
        (255, 255, 255))

    def __init__(self):
        pass


class GameFonts(object):
    large_font = pygame.font.SysFont('Banschrift Light Semicondensed', 24, False, False)
    small_font = pygame.font.SysFont('Banschrift Light Semicondensed', 18, False, False)

    def __init__(self):
        pass


class RenderParameters(object):
    def __init__(self, screen_dimensions, map_size, image_size):
        self.screen_width = screen_dimensions[0]
        self.screen_height = screen_dimensions[1]
        self.map_size = map_size
        self.image_size = image_size

        self.margin = 0
        self.lod = 3.0
        self.scale = 0.4
        self.scroll_x = 0
        self.scroll_y = 0

        # Booleans for pictorial rendering
        self.render_buildings = True
        self.render_roads = True
        self.render_plaza = False
        # Booleans for rendering map mesh junk
        self.mesh_mode = False
        self.render_delaunay_tris = False
        self.render_points = False
        self.render_edge_points = False
        self.render_region_borders = False
        self.render_filled_edge_regions = False

    def toggle_mesh_mode(self):
        self.mesh_mode = not self.mesh_mode


colors = Colors()
gf = GameFonts()


def segment_to_polygon_pts(pt_A, pt_B, thickness):
    """Returns a 4-tuple of px coordinate pairs with values offset for display"""
    angle = math.atan2(pt_A[1] - pt_B[1], pt_A[0] - pt_B[0])
    center_pt = ((pt_A[0] + pt_B[0]) / 2., (pt_A[1] + pt_B[1]) / 2.)
    length = util.get_length(pt_A, pt_B)
    UL = (center_pt[0] + (length / 2.) * math.cos(angle) -
          (thickness / 2.) * math.sin(angle),
          center_pt[1] + (thickness / 2.) * math.cos(angle) +
          (length / 2.) * math.sin(angle))
    UR = (center_pt[0] - (length / 2.) * math.cos(angle) -
          (thickness / 2.) * math.sin(angle),
          center_pt[1] + (thickness / 2.) * math.cos(angle) -
          (length / 2.) * math.sin(angle))
    BL = (center_pt[0] + (length / 2.) * math.cos(angle) +
          (thickness / 2.) * math.sin(angle),
          center_pt[1] - (thickness / 2.) * math.cos(angle) +
          (length / 2.) * math.sin(angle))
    BR = (center_pt[0] - (length / 2.) * math.cos(angle) +
          (thickness / 2.) * math.sin(angle),
          center_pt[1] - (thickness / 2.) * math.cos(angle) -
          (length / 2.) * math.sin(angle))
    return (UL, BL, BR, UR)


def render_points(render_surface, lod, city, offset, mesh_mode):
    point_image = pygame.Surface((1 * lod, 1 * lod))
    point_image.fill(colors.points[mesh_mode])
    # Render red dots for each centroid
    for point in city.points:
        # -2 to recenter the points by half the width of the point image
        render_surface.blit(
            point_image,
            [int(point[0] * lod) + offset - 0.5 * lod,
             int(point[1] * lod) + offset - 0.5 * lod])


def render_region_borders(render_surface, lod, city, offset, mesh_mode):
    # Render each voronoi region polygon in white
    for region in city.vor.regions:
        # skip regions with fewer than 3 points or with points off the coordinate field (-1)
        if len(region) < 3:
            continue
        if -1 in region:
            continue
        else:
            # store the points from each polygon
            edge_points = []
            for vertex_index in region:
                edge_points.append(city.vor.vertices[vertex_index])
        # even_squares = [x * x for x in range(10) if x % 2 == 0]

        # apply a rendering offset half the width / height of the coordinate field
        adjusted_edge_points = []
        for edge_point in edge_points:
            adjusted_edge_points.append(
                (int(edge_point[0] * lod) + offset,
                 int(edge_point[1] * lod) + offset))

        # render a closed polygon for each voronoi region's points
        pygame.draw.aalines(
            render_surface,
            colors.region_borders[mesh_mode],
            True,
            adjusted_edge_points)


def render_delaunay_edges(render_surface, lod, city, offset, mesh_mode):
    # Render Each Delaunay Edge in Blue
    for i, simplex in enumerate(city.dela.simplices):
        simplex_points = []
        for point in city.vor.points[city.dela.simplices[i]]:
            simplex_points.append(point)
        adjusted_simplex_points = []
        for simplex_point in simplex_points:
            adjusted_simplex_points.append(
                (int(simplex_point[0] * lod) + offset,
                 int(simplex_point[1] * lod) + offset))
        pygame.draw.aalines(
            render_surface,
            colors.delaunay_edges[mesh_mode],
            True,
            adjusted_simplex_points)


def render_edge_points(render_surface, lod, city, offset, mesh_mode):
    edge_point_image = pygame.Surface((1 * lod, 1 * lod))
    edge_point_image.fill(colors.edge_points[mesh_mode])

    # Render Each Border Point in Green
    for point in city.edge_regions.all():
        x = point[0] * lod + offset - 0.5 * lod
        y = point[1] * lod + offset - 0.5 * lod
        render_surface.blit(
            edge_point_image,
            [int(x), int(y)])


def render_plaza(render_surface, lod, city, offset, mesh_mode):
    plaza_image = pygame.Surface((1 * lod, 1 * lod))
    plaza_image.fill(colors.plaza[mesh_mode])
    region_index = util.coordinates_to_region_index(
        city.vor,
        city.structures.center_plaza)
    adjusted_polygon_points = []
    for vertex_index in city.vor.regions[region_index]:
        # Skip any corners off the edge
        if vertex_index == -1:
            continue
        xy_pair = city.vor.vertices[vertex_index]
        adjusted_polygon_points.append((
            int(xy_pair[0] * lod) + offset,
            int(xy_pair[1] * lod) + offset))

    pygame.gfxdraw.filled_polygon(
        render_surface,
        adjusted_polygon_points,
        colors.plaza_fill[mesh_mode])

    render_surface.blit(plaza_image, [
        int(city.structures.center_plaza[0] * lod) + offset - 0.5 * lod,
        int(city.structures.center_plaza[1] * lod) + offset - 0.5 * lod])


def render_filled_edge_regions(render_surface, lod, city, offset, mesh_mode):
    # render each border region in green
    for edge_region in city.edge_regions.all():
        region_index = util.coordinates_to_region_index(city.vor, edge_region)
        adjusted_polygon_points = []
        for vertex_index in city.vor.regions[region_index]:
            # Skip any corners off the edge
            if vertex_index == -1:
                continue
            xy_pair = city.vor.vertices[vertex_index]
            adjusted_polygon_points.append((
                int(xy_pair[0] * lod) + offset,
                int(xy_pair[1] * lod) + offset))
        # skip any polygons with fewer than 3 sides / corners
        if len(adjusted_polygon_points) < 3:
            continue

        pygame.gfxdraw.filled_polygon(
            render_surface,
            adjusted_polygon_points,
            colors.edge_region_fill[mesh_mode])


def render_roads(render_surface, lod, city, offset, mesh_mode):
    # Render Roads as adjustable pxl width polygons
    road_segment_groups = []
    for road in city.structures.major_roads:
        road_segments = []
        for node in road:
            # don't try to render the first point in a segment
            if node[1] is None:
                continue

            pt_A = node[0]
            pt_B = node[1]

            raw_pts = segment_to_polygon_pts(pt_A, pt_B, (4 / lod))
            segment_points = []
            for raw_point in raw_pts:
                segment_points.append((int(raw_point[0] * lod) + offset,
                                       int(raw_point[1] * lod) + offset))
            road_segments.append(segment_points)
        # append a final fake rendering node to make it seem like the roads go off the edge of the map
        pt_A = road[-1][0]
        closest_edge = util.get_closest_edge(city.map_size, pt_A)
        if closest_edge == 0:
            pt_B = (pt_A[0] + random.randint(-10, 10), -int(city.map_size * 0.5))
        elif closest_edge == 1:
            pt_B = (pt_A[0] + random.randint(-10, 10), int(city.map_size * 0.5))
        elif closest_edge == 2:
            pt_B = (-int(city.map_size * 0.5), pt_A[1] + random.randint(-10, 10))
        elif closest_edge == 3:
            pt_B = (int(city.map_size * 0.5), pt_A[1] + random.randint(-10, 10))
        raw_pts = segment_to_polygon_pts(pt_A, pt_B, (4 / lod))
        segment_points = []
        for raw_point in raw_pts:
            segment_points.append((int(raw_point[0] * lod) + offset,
                                   int(raw_point[1] * lod) + offset))
        road_segments.append(segment_points)

        # add the rendering points for the total road to the bag of road polygons to render
        road_segment_groups.append(road_segments)

    for road in city.structures.minor_roads:
        road_pts = []
        road_segments = []
        for node in road:
            # switch code for rendering minor roads with polygons - useful for larger map render sizes
            if lod <= 1.5:
                road_pts.append(
                    (int(node[0][0] * lod) + offset,
                     int(node[0][1] * lod) + offset))
                continue
            # don't try to render the first point in a segment
            if node[1] is None:
                continue

            pt_A = node[0]
            pt_B = node[1]

            raw_pts = segment_to_polygon_pts(pt_A, pt_B, (2 / lod))
            segment_points = []
            for raw_point in raw_pts:
                segment_points.append((int(raw_point[0] * lod) + offset,
                                       int(raw_point[1] * lod) + offset))
            road_segments.append(segment_points)
        road_segment_groups.append(road_segments)
        if lod <= 1.5:
            pygame.draw.lines(
                render_surface,
                colors.minor_road[mesh_mode],
                False,
                road_pts)

    for road_segments in road_segment_groups:
        for segment_points in road_segments:
            pygame.gfxdraw.aapolygon(
                render_surface,
                segment_points,
                colors.major_road[mesh_mode])
            pygame.gfxdraw.filled_polygon(
                render_surface,
                segment_points,
                colors.major_road[mesh_mode])


def render_buildings(render_surface, lod, city, offset, mesh_mode):
    buildings = []
    for (dense, simplex) in city.structures.building_simplices:
        adjusted_polygon_points = []
        for vertex in simplex:
            xy_pair = city.dela.points[vertex]
            adjusted_polygon_points.append((
                int(xy_pair[0] * lod) + offset,
                int(xy_pair[1] * lod) + offset))
        buildings.append((dense, adjusted_polygon_points))
    for (dense, polygon_pts) in buildings:
        color = colors.low_density[mesh_mode]
        if dense:
            color = colors.high_density[mesh_mode]
        pygame.gfxdraw.aapolygon(
            render_surface,
            polygon_pts,
            color)
        pygame.gfxdraw.filled_polygon(
            render_surface,
            polygon_pts,
            color)


def render_image(city, render_parameters):
    rp = render_parameters
    render_surface = pygame.Surface(
        [int(rp.image_size * rp.lod + rp.margin * 2),
         int(rp.image_size * rp.lod + rp.margin * 2)])
    render_surface.fill(colors.background[rp.mesh_mode])
    # this moves all rendered points onto the visible surface area
    # by default the coordinates will be inverted by half the image size
    offset = int(rp.image_size * rp.lod * 0.5 + rp.margin) 

    if rp.render_buildings:
        render_buildings(
            render_surface,
            rp.lod,
            city,
            offset,
            rp.mesh_mode)
    if rp.render_roads:
        render_roads(
            render_surface,
            rp.lod,
            city,
            offset,
            rp.mesh_mode)
    if rp.render_plaza:
        render_plaza(
            render_surface,
            rp.lod,
            city,
            offset,
            rp.mesh_mode)
    if rp.render_delaunay_tris:
        render_delaunay_edges(
            render_surface,
            rp.lod,
            city,
            offset,
            rp.mesh_mode)
    if rp.render_points:
        render_points(
            render_surface, rp.lod, city, offset, rp.mesh_mode)
    if rp.render_edge_points:
        render_edge_points(
            render_surface, rp.lod, city, offset, rp.mesh_mode)
    if rp.render_region_borders:
        render_region_borders(
            render_surface,
            rp.lod,
            city,
            offset,
            rp.mesh_mode)
    if rp.render_filled_edge_regions:
        render_filled_edge_regions(
            render_surface,
            rp.lod,
            city,
            offset,
            rp.mesh_mode)

    return render_surface


def render_user_interface(screen, state):
    def on_off_string(on):
        if on:
            return "on"
        return "off"

    rp = state.render_parameters
    lines = [
        "City Size: {0}".format(state.city.size),
        "Map Size: {0}".format(state.city.map_size),
        "Major Roads: {0}, Minor Roads: {1}".format(
            state.gen_parameters.n_majroads,
            state.gen_parameters.n_minroads),
        "Fill Roads: {0}".format(state.gen_parameters.n_fillroads),
        "Render Settings",
        "__________________",
        "Mesh View Mode: {0}".format(on_off_string(rp.mesh_mode)),
        "Rendering Delaunay Tris: {0}".format(on_off_string(rp.render_delaunay_tris)),
        "Rendering Points: {0}".format(on_off_string(rp.render_points)),
        "Rendering Edge Points: {0}".format(on_off_string(rp.render_edge_points)),
        "Rendering Region Borders: {0}".format(on_off_string(rp.render_region_borders)),
        "Rendering Filled Edge Regions: {0}".format(
            on_off_string(rp.render_filled_edge_regions)),
        "Rendering Buildings: {0}".format(on_off_string(rp.render_buildings)),
        "Rendering Roads: {0}".format(on_off_string(rp.render_roads)),
        "Rendering Plaza: {0}".format(on_off_string(rp.render_plaza))]
    for i, line in enumerate(lines):
        screen.blit(
            gf.large_font.render(line, True, (255, 255, 255)),
            [state.screen_width - 290, 10 + 24 * i])



def render_message_screen(screen_dimensions, message_string):
    message_screen = pygame.Surface(
        [screen_dimensions[0] - 300,
         screen_dimensions[1] - 20])
    message_screen.fill((20, 20, 20))
    render_surface.blit(
        gf.large_font.render(message_string,
                             True,
                             (205, 205, 205)),
        [20, 20])

    return render_surface


def rescale_map_image(max_lod_image, image_size, scale):
    scaled_map_image = pygame.Surface(
        [int(image_size * scale),
         int(image_size * scale)])
    scaled_map_image = pygame.transform.smoothscale(max_lod_image,
        [int(image_size * scale),
         int(image_size * scale)])
    return scaled_map_image


def display_update(state, screen, screen_dimensions, scroll_x, scroll_y):
    rp = state.render_parameters
    # reset and wipe screen
    screen.fill(colors.bg_blue)
    preview_window = pygame.Surface(
        [screen_dimensions[0] - 300,
         screen_dimensions[1] - 20])
    preview_window.fill((20, 20, 20))
    preview_window.blit(state.cached_map_image, [scroll_x, scroll_y])
    screen.blit(preview_window, [0, 0])
    render_user_interface(screen, state)
    # close out and frame limit
    pygame.display.flip()
    state.clock.tick(60)
