import math
import time


class VisibleGrid:
    def __init__(self, x1, y1, x2, y2, padding, factor):
        self.padding = padding
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.w = max(0, self.x2 - self.x1)
        self.h = max(0, self.y2 - self.y1)
        self.id = f"{x1}-{y1}-{x2}-{y2}-{factor}"
        self.factor = factor
        self.offset_x = x1
        self.offset_y = y1

        #
        #
        # self.scaled_x1 = int(x1 / node_gap)
        # self.scaled_y1 = int(y1 / node_gap)
        # self.scaled_x2 = math.ceil(x2 / node_gap)
        # self.scaled_y2 = math.ceil(y2 / node_gap)
        # self.scaled_w = max(0,self.scaled_x2 - self.scaled_x1)
        # self.scaled_h = max(0,self.scaled_y2 - self.scaled_y1)
        #
        # self.scaled_offset_x = self.scaled_x1 * node_gap
        # self.scaled_offset_y = self.scaled_y1 * node_gap
        self.bsp_leaf_id = None

    def contains(self, x1, y1, x2, y2, factor):
        n_w = x2 - x1
        n_h = y2 - y1

        return (x1 >= self.x1
                and y1 >= self.y1
                and x2 <= self.x2
                and y2 <= self.y2
                and max(0, self.w - 4 * self.padding) <= n_w
                and max(0, self.h - 4 * self.padding) <= n_h
                and factor == self.factor)


class NViewport:
    def __init__(self, n_tree, buffer_w, buffer_h):
        self.visible_data = None
        self.n_tree = n_tree
        self.x1 = 0
        self.y1 = 0
        self.x2 = 0
        self.y2 = 0
        self.buffer_w = buffer_w
        self.buffer_h = buffer_h

        self.use_bsp = False

    def set_grid_size(self, width, height):
        self.x2 = width
        self.y2 = height

        if self.use_bsp:
            self.n_tree.set_size(width, height)
            self.n_tree.generate()

    def get_details_factor(self, viewport):
        """
        Calculate the down sample factor
        Factor is used to reduce the vertices count or texture quality

        Compare screen space bounds with world grid bounds
        """
        x, y, w, h, zoom = viewport
        col_min = x
        row_min = y
        col_max = x + w
        row_max = y + h

        subgrid_width = (col_max - col_min)
        subgrid_height = (row_max - row_min)

        target_width = self.buffer_w
        target_height = self.buffer_h

        width_factor = max(subgrid_width / target_width, 0.1)
        height_factor = max(subgrid_height / target_height, 0.1)
        factor = max(width_factor, height_factor)
        return math.ceil(factor)

    def update_viewport(self, viewport):

        # Legacy solution
        # Calculating grid bounds from viewport is less expensive than traversing the bsp tree
        if self.use_bsp:
            self.n_tree.update_viewport(viewport)
            if self.n_tree.mega_leaf is None:
                return
            if self.visible_data is None or self.visible_data.bsp_leaf_id != self.n_tree.mega_leaf.id:
                factor = self.get_details_factor(viewport)
                self.visible_data = VisibleGrid(
                    self.n_tree.mega_leaf.x1,
                    self.n_tree.mega_leaf.y1,
                    self.n_tree.mega_leaf.x2,
                    self.n_tree.mega_leaf.y2,
                    0,
                    factor)
                self.visible_data.bsp_leaf_id = self.n_tree.mega_leaf.id
            return

        # Grid bounds from viewport

        start_time = time.time()
        x, y, w, h, zoom = viewport

        x1 = int(max(x, self.x1))
        y1 = int(max(y, self.y1))
        x2 = math.ceil(min(x + w, self.x2))
        y2 = math.ceil(min(y + h, self.y2))
        width = x2 - x1
        height = y2 - y1
        factor = self.get_details_factor(viewport)
        padding = int(w / 6)
        updated = False

        if self.visible_data is None or not self.visible_data.contains(x1, y1, x2, y2, factor):
            self.visible_data = VisibleGrid(
                max(0, x1 - padding),
                max(0, y1 - padding),
                min(x1 - padding + width + 2 * padding, self.x2),
                min(y1 - padding + height + 2 * padding, self.y2),
                padding,
                factor)
            updated = True

        if updated:
            print("Visible grid updated",
                  "x1", self.visible_data.x1,
                  "y1", self.visible_data.y1,
                  "w", self.visible_data.w,
                  "h", self.visible_data.h,
                  "factor", factor)
