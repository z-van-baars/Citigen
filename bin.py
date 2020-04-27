

def reconstruct_polygon(map_size, corners):
    prev_corner = -1
    revised_corners = []
    print(corners)
    for corner_index, corner in enumerate(corners):
        if corner is not -1:
            prev_corner = corner
            revised_corners.append(corner)
        elif corner is -1:
            if prev_corner is -1:
                prev_corner = corners[-1]
                if prev_corner is -1:
                    prev_corner = corners[-2]

            assert prev_corner is not -1

            new_corner = []
            closest_edge = get_closest_edge(map_size, prev_corner)
            if closest_edge is 0:
                # top of map
                new_corner = [prev_corner[0], -map_size * 0.5]
            elif closest_edge is 1:
                # left of map
                new_corner = [-map_size * 0.5, prev_corner[1]]
            elif closest_edge is 2:
                # right of map
                new_corner = [map_size * 0.5, prev_corner[1]]
            elif closest_edge is 3:
                # bottom of map
                new_corner = [prev_corner[0], map_size * 0.5]
            revised_corners.append(new_corner)
    corners = revised_corners
    return revised_corners


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


    def get_edges_programmatic(self):
        border_regions = []
        for x in range(self.map_size):
            distances_top = []
            distances_bottom = []
            # print(-int(self.map_size / 2) + x, -int(self.map_size / 2))
            for each_point in self.points:
                dist_t = get_length((-int(self.map_size / 2) + x, -int(self.map_size / 2)), each_point)
                dist_b = get_length((-int(self.map_size / 2) + x, int(self.map_size / 2)), each_point)
                dist_t = round(dist_t, 2)
                dist_b = round(dist_b, 2)
                distances_top.append((dist_t, each_point))
                distances_bottom.append((dist_b, each_point))
            distances_top_sorted = sorted(distances_top, key=lambda d: d[0])
            distances_bottom_sorted = sorted(distances_bottom, key=lambda d: d[0])
            border_regions.append(distances_top_sorted[0][1])
            border_regions.append(distances_bottom_sorted[0][1])
        for y in range(self.map_size):
            distances_left = []
            distances_right = []
            for each_point in self.points:
                dist_l = get_length((-int(self.map_size / 2), -int(self.map_size / 2) + y), each_point)
                dist_r = get_length((int(self.map_size / 2), -int(self.map_size / 2) + y), each_point)
                dist_l = round(dist_l, 2)
                dist_r = round(dist_r, 2)
                distances_left.append((dist_l, each_point))
                distances_right.append((dist_r, each_point))
            distances_left_sorted = sorted(distances_left, key=lambda d: d[0])
            distances_right_sorted = sorted(distances_right, key=lambda d: d[0])
            border_regions.append(distances_left_sorted[0][1])
            border_regions.append(distances_right_sorted[0][1])
        print(border_regions)
        border_regions_sifted = []

        return border_regions
