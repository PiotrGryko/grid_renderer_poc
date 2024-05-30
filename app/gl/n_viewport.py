import math
import time


class VisibleGrid:
    """
    Visible data bounds (world bounds)
    Factor represents the details factor
    for example if factor is 10, it will fetch every 10th row and column
    """

    def __init__(self, x1, y1, x2, y2, padding, factor, zoom):
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

        self.zoom = zoom
        self.bsp_leaf_id = None

        # x1, x2, y1, y2 represent the WORLD bounds
        # Factor N means that the data inside bounds is sampled every N row and column
        # by dividing bounds by N we get the actual data bounds
        # The content of these bounds is the data that is written to texture and send to shader

        # Normalized data (without any gaps, translated to 0,0) is written to fixed size texture (size 0,0,2560,2560)
        # The quad position in the world is VisibleGrid.offset + (0,0,2560,2560) * factor
        # Texture is mapped to a quad and drawn on the screen

        # Normalized bounds to a grid with factor 1
        self.fx1 = int(self.x1 / factor)
        self.fx2 = math.ceil(self.x2 / factor)
        self.fy1 = int(self.y1 / factor)
        self.fy2 = math.ceil(self.y2 / factor)

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
    def __init__(self, n_tree, n_net, buffer_w, buffer_h):
        self.visible_data = None
        self.n_tree = n_tree
        self.n_net = n_net
        self.x1 = 0
        self.y1 = 0
        self.x2 = 0
        self.y2 = 0
        self.buffer_w = buffer_w
        self.buffer_h = buffer_h

        self.use_bsp = False

        self.current_factor = None
        self.current_factor_delta = None
        self.current_factor_half_delta = 1
        self.power_of_two = True

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

        subgrid_width = min(col_max - col_min, self.n_net.total_width)
        subgrid_height = min(row_max - row_min, self.n_net.total_height)

        target_width = self.buffer_w
        target_height = self.buffer_h

        width_factor = max(subgrid_width / target_width, 0.1)
        height_factor = max(subgrid_height / target_height, 0.1)
        factor = max(width_factor, height_factor)

        if self.power_of_two:
            lower_power = 2 ** math.floor(math.log2(factor))
            higher_power = lower_power * 2
            if higher_power <= 0.5:
                higher_power = 0.5
                self.current_factor_half_delta = (factor - lower_power) / (higher_power - lower_power)
            else:
                self.current_factor_half_delta = 1

            if higher_power <= 1:
                higher_power = 1
                lower_power = 0.1
            self.current_factor = math.ceil(higher_power)
            self.current_factor_delta = (factor - lower_power) / (higher_power - lower_power)

        else:
            self.current_factor = math.ceil(factor)
            self.current_factor_delta = factor - math.ceil(factor)

        return self.current_factor, self.current_factor_delta

    def update_viewport(self, viewport):

        start_time = time.time()
        x, y, w, h, zoom = viewport

        x1 = int(max(x, self.x1))
        y1 = int(max(y, self.y1))
        x2 = math.ceil(min(x + w, self.x2))
        y2 = math.ceil(min(y + h, self.y2))
        width = x2 - x1
        height = y2 - y1
        factor, fraction = self.get_details_factor(viewport)
        padding = int(w / 6)
        updated = False

        if self.visible_data is None or not self.visible_data.contains(x1, y1, x2, y2, factor):
            self.visible_data = VisibleGrid(
                max(0, x1 - padding),
                max(0, y1 - padding),
                min(x1 - padding + width + 2 * padding, self.x2),
                min(y1 - padding + height + 2 * padding, self.y2),
                padding,
                factor,
                zoom)
            updated = True

        if updated:
            print("Visible grid updated",
                  "x1", self.visible_data.x1,
                  "y1", self.visible_data.y1,
                  "w", self.visible_data.w,
                  "h", self.visible_data.h,
                  "factor", factor)
