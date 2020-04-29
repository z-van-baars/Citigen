import random
import util
import time
from scipy.spatial import Voronoi, Delaunay


class Structures(object):
    def __init__(self):
        self.initialize_all()

    def initialize_all(self):
        self.major_roads = []
        self.minor_roads = []
        self.center_plaza = []
        self.small_plazas = []
        self.markets = []  #
        self.cathedrals = []  #
        self.castles = []  #
        self.docks = []  #
        self.wells = []  #
        self.guild_halls = []  #
        self.core_locations = []
        self.farms = []  #
        self.building_simplices = []
        self.low_density_blocks = []  #
        self.high_density_blocks = []  #


class EdgeRegions(object):
    def __init__(self):
        self.top = []
        self.bottom = []
        self.left = []
        self.right = []

    def all(self):
        return self.top + self.bottom + self.left + self.right


class City(object):
    def __init__(self, map_size, size, walls):
        self.structures = Structures()
        self.size = size  # 1 village, 2 town, 3 city, 4 metro
        self.map_size = map_size
        self.walls = walls  # 0 no walls, 1 small walls, 2 large walls
        self.points = []
        self.edge_regions = None
        self.road_segments = {}
        self.vor = None
        self.dela = None

    def initalize_blank_map(self):
        self.structures.initialize_all()

    def cull_points(self, map_size):
        def is_within_borders(map_size, point):
            return (-map_size * 0.5 <= point[0] < map_size * 0.5 and
                    -map_size * 0.5 <= point[1] < map_size * 0.5)
        interior_points = []
        for point in self.points:
            if is_within_borders(map_size, point):
                interior_points.append(point)
        self.points = interior_points

    def gen_random_pts(self):
        self.points = []
        n_points = max(self.size, 2) * self.map_size
        for i in range(int(n_points)):
            self.points.append(util.generate_coordinate_pair([
                int(-self.map_size * 0.5),
                int(self.map_size * 0.5)]))

        # add a second and third crop of points in a central radius for density purposes
        for i, r in enumerate([self.map_size * 0.4, self.map_size * 0.2]):
            for pt in range(int(n_points * 0.30 * (0.15 + 0.6 * i))):
                while True:
                    xy = util.generate_coordinate_pair(
                        [int(-self.map_size * 0.5),
                         int(self.map_size * 0.5)])
                    if util.get_length(xy, [0, 0]) < r:
                        self.points.append(xy)
                        break

        self.vor = Voronoi(self.points)
        self.dela = Delaunay(self.points)
        print("Points: {0}, Vertices: {1}, Simplices: {2}".format(
            len(self.dela.points),
            len(self.dela.vertices),
            len(self.dela.simplices)))

    def get_edge_regions(self):
        self.edge_regions = EdgeRegions()
        edge_region_indices = []
        # get edge regions who have polygon points outside the voronoi graph
        for index, region in enumerate(self.vor.point_region):
            region_points = self.vor.regions[region]
            if -1 in region_points:
                edge_region_indices.append(index)
                # print(self.vor.points[index])
            else:
                for pt_index in region_points:
                    xy_coords = self.vor.vertices[pt_index]
                    if any([xy_coords[0] < -self.map_size * 0.5,
                            xy_coords[0] >= self.map_size * 0.5,
                            xy_coords[1] < -self.map_size * 0.5,
                            xy_coords[1] >= self.map_size * 0.5]):
                        edge_region_indices.append(index)
        # remove duplicates if any
        unique_edge_regions = list(dict.fromkeys(edge_region_indices))

        edge_region_coordinates = list(
            self.vor.points[point_index] for point_index in unique_edge_regions)
        for coord in edge_region_coordinates:
            edge_id = util.get_closest_edge(self.map_size, coord)
            if edge_id == 0:
                self.edge_regions.top.append(coord)
            elif edge_id == 1:
                self.edge_regions.bottom.append(coord)
            elif edge_id == 2:
                self.edge_regions.left.append(coord)
            elif edge_id == 3:
                self.edge_regions.right.append(coord)

    def relax_points(self):
        self.points = util.lloyd_relaxation(self.vor)
        self.cull_points(self.map_size)
        self.vor = Voronoi(self.points)
        self.dela = Delaunay(self.points)
        self.get_edge_regions()

    def collect_central_points(self, vor, size, map_size, inner_radius, outer_radius):
        inner_city_points = []
        outer_city_points = []

        for point in vor.points:
            if util.get_length([0, 0], point) < inner_radius:
                inner_city_points.append(point)
            if util.get_length([0, 0], point) < outer_radius:
                outer_city_points.append(point)
        return inner_city_points, outer_city_points

    def generate_core(self, inner_city_points):
        chosen_points = []

        self.structures.center_plaza = self.choose_center_plaza(
            self.map_size,
            self.size,
            inner_city_points)
        chosen_points.append(self.structures.center_plaza)

        cp_index = util.coordinates_to_point_index(
            self.vor, self.structures.center_plaza)

        self.structures.well = self.choose_well(
            util.get_neighbors(
                self.dela,
                cp_index))

        self.structures.small_plazas = []
        for sp in range(3):
            while True:
                new_point = random.choice(inner_city_points)
                if not util.coord_list_match(chosen_points, new_point):
                    chosen_points.append(new_point)
                    break
            self.structures.small_plazas.append(new_point)
        self.structures.core_locations += self.structures.small_plazas
        self.structures.core_locations += [self.structures.well]
        self.structures.core_locations += [self.structures.center_plaza]

    def choose_center_plaza(self, map_size, size, inner_city_points):
        assert len(inner_city_points) > 1
        center_plaza_radius = map_size * (0.05 + 0.01 * size)
        while True:
            center_plaza = random.choice(inner_city_points)
            if center_plaza_radius >= util.get_length([0, 0], center_plaza):
                break
        return center_plaza

    def choose_well(self, plaza_neighbors):
        return self.vor.points[random.choice(plaza_neighbors)]

    def generate_road(self, vor, dela, start_point, end_point):
        prev_node_index = util.coordinates_to_point_index(vor, start_point)
        new_road = [(start_point, None)]
        # incrementally path to end point, greedy first
        while True:
            new_neighbors = util.get_neighbors(
                dela,
                prev_node_index)
            assert len(new_neighbors) > 0

            # there's a bug here, it sometimes crashes
            # theories are that potentially point [0, 0] is being added to potential start points
            # or potentially the central plaza point is being added to potential start points
            # print("Neighbors", new_neighbors, "Previous Node Index: {0}".format(prev_node_index))
            # print("Previous Node Coords: {0}".format(vor.points[prev_node_index]))

            # check which of our neighbors is the closest to the end point
            new_neighbor_distances = []
            for new_neighbor in new_neighbors:
                dist1 = util.get_length(
                    end_point,
                    vor.points[new_neighbor])
                new_neighbor_distances.append((dist1, new_neighbor))
            new_node_index = sorted(new_neighbor_distances, key=lambda d: d[0])[0][1]
            # pin the new node along the path and the previous node to the road nodes list
            new_road.append((vor.points[new_node_index],
                             vor.points[prev_node_index]))
            prev_node_index = new_node_index
            if (
                vor.points[new_node_index][0] == end_point[0] and
                vor.points[new_node_index][1] == end_point[1]
            ):
                return new_road

    def generate_major_roads(self, n_majroads, vor, dela, edge_regions, core_locations):
        edge_lists = [edge_regions.top,
                      edge_regions.bottom,
                      edge_regions.left,
                      edge_regions.right]

        for r in range(n_majroads):
            new_road = []
            # some funky junk modulo math so we pick a smattering of different edges
            if r > 3:
                edge_terminus = random.choice(edge_lists[(r % 4)])
            elif r <= 3:
                edge_terminus = random.choice(edge_lists[r])

            new_road = self.generate_road(
                vor,
                dela,
                random.choice(core_locations),
                edge_terminus)
            self.structures.major_roads.append(new_road)

    def generate_minor_roads(self,
                             n_minroads,
                             major_roads,
                             vor,
                             dela,
                             inner_radius,
                             outer_radius,
                             inner_city_points,
                             outer_city_points):
        print("Generating Minor Roads")
        start = time.time()
        available_end_nodes = []
        for road in major_roads:
            for node in road:
                if util.get_length([0, 0], node[0]) < outer_radius:
                    available_end_nodes.append(node[0])
        assert len(available_end_nodes) > 0
        # make a new road with a randomized end point
        # smashing through / across existing roads is specifically allowed
        # the chaotic nature of the output is a good compromise between speed
        # and realism
        for r in range(n_minroads):
            start_point = random.choice(outer_city_points)
            # choose random end point for speed
            end_point = random.choice(available_end_nodes)
            new_road = self.generate_road(vor, dela, start_point, end_point)
            self.structures.minor_roads.append(new_road)

        end = time.time()
        print("Elapsed time: {0}s".format(round(end - start, 2)))

    def generate_fill_roads(self,
                            n_fillroads,
                            major_roads,
                            minor_roads,
                            vor,
                            dela,
                            inner_city_points,
                            outer_city_points):
        print("Generating Fill Roads")
        start = time.time()
        all_road_nodes = []
        for road in major_roads + minor_roads:
            for node in road:
                all_road_nodes.append(node[0])
        for r in range(n_fillroads):
            start_point = random.choice(inner_city_points)
            node_distances = []
            end_point = True
            # find end point by distance
            for node in all_road_nodes:
                if tuple(node) == tuple(start_point):
                    end_point = False
                    break
                node_distances.append((util.get_length(start_point, node), node))
            if end_point is False:
                continue
            end_point = sorted(node_distances, key=lambda d: d[0])[0][1]
            new_road = self.generate_road(vor, dela, start_point, end_point)
            self.structures.minor_roads.append(new_road)
            for node in new_road:
                all_road_nodes.append(node[0])
        end = time.time()
        print("Elapsed time: {0}s".format(round(end - start, 2)))

    def extend_roads(self, major_roads, minor_roads, vor, dela):
        def extend_road(min_road, all_road_nodes, neighbor_node_coords):
            chance_to_connect = 85
            for neighbor_node in neighbor_node_coords:
                for road_node in all_road_nodes:
                    if tuple(neighbor_node) == tuple(road_node):
                        if random.randint(1, 100) < chance_to_connect:
                            min_road.append((road_node, min_road[-1][0]))
                            return

        print("Extending Roads")
        # extend minor roads by one segment if there is an existing road node within 1 neighbor
        for i, min_road in enumerate(minor_roads):
            final_node_index = util.coordinates_to_point_index(vor, min_road[-1][0])
            neighbor_nodes = util.get_neighbors(
                dela,
                final_node_index)
            neighbor_node_coords = []
            for node_index in neighbor_nodes:
                neighbor_node_coords.append(vor.points[node_index])

            all_road_nodes = []
            for j, road in enumerate(minor_roads):
                if j == i:
                    continue
                for node in road:
                    all_road_nodes.append(node[0])
            extend_road(min_road, all_road_nodes, neighbor_node_coords)

    def log_road_segments(self, vor, dela, major_roads, minor_roads):
        road_segments = {}
        road_nodes = []
        for major_road in major_roads:
            for node in major_road:
                road_nodes.append(tuple(node[0]))
                if node[1] is None:
                    continue
                # assertion fails because roads can be duplicated
                # assert (tuple(node[1]), tuple(node[0])) not in road_segments
                road_segments[(tuple(node[1]), tuple(node[0]))] = True
        for minor_road in minor_roads:
            for node in minor_road:
                road_nodes.append(tuple(node[0]))
                if node[1] is None:
                    continue
                # assert (tuple(node[1]), tuple(node[0])) not in road_segments
                road_segments[(tuple(node[1]), tuple(node[0]))] = False
        unique_road_nodes = list(dict.fromkeys(road_nodes))
        self.road_segments = road_segments
        self.road_nodes = unique_road_nodes

    def generate_blocks(self, vor, dela, road_segments, road_nodes):
        building_simplices = []
        for simplex in dela.simplices:
            is_building = False
            v = 0
            for i, vertex_index in enumerate(simplex):
                if tuple(vor.points[vertex_index]) in road_nodes:
                    is_building = True
                    if v == 0:
                        v = 1
                a = tuple(vor.points[simplex[i]])
                if i == 2:
                    b = tuple(vor.points[simplex[0]])
                else:
                    b = tuple(vor.points[simplex[i + 1]])

                if (a, b) in road_segments:
                    is_building = True
                    if road_segments[(a, b)] is True:
                        v += 1
                    elif road_segments[(a, b)] is False:
                        v += 1
                    else:
                        print("Test Failed")
                elif (a, b) not in road_segments and (b, a) in road_segments:
                    is_building = True
                    if road_segments[(b, a)] is True:
                        v += 1
                    elif road_segments[(b, a)] is False:
                        v += 1
                    else:
                        print("Test Failed")

            # disallow edge tris from being added to building groups
            for neighbor in dela.neighbors[simplex]:
                if neighbor is -1:
                    is_building = False

            if is_building:
                if v >= 3:
                    building_simplices.append((True, simplex))
                    continue
                building_simplices.append((False, simplex))

        self.structures.building_simplices = building_simplices

    def generate_structures(self, gen_parameters):
        gp = gen_parameters

        inner_city_points, outer_city_points = self.collect_central_points(
            self.vor,
            self.size,
            self.map_size,
            gp.inner_radius,
            gp.outer_radius,)
        self.generate_core(inner_city_points)
        self.generate_major_roads(
            gp.n_majroads,
            self.vor,
            self.dela,
            self.edge_regions,
            self.structures.core_locations)
        self.generate_minor_roads(
            gp.n_minroads,
            self.structures.major_roads,
            self.vor,
            self.dela,
            gp.inner_radius,
            gp.outer_radius,
            inner_city_points,
            outer_city_points)
        self.generate_fill_roads(
            gp.n_fillroads,
            self.structures.major_roads,
            self.structures.minor_roads,
            self.vor,
            self.dela,

            inner_city_points,
            outer_city_points)
        self.extend_roads(
            self.structures.major_roads,
            self.structures.minor_roads,
            self.vor,
            self.dela)
        self.log_road_segments(
            self.vor,
            self.dela,
            self.structures.major_roads,
            self.structures.minor_roads)
        self.generate_blocks(
            self.vor,
            self.dela,
            self.road_segments,
            self.road_nodes)
