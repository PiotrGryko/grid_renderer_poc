from app.gl.n_scene_entity import EntityV2


class NSceneV2:
    def __init__(self, n_net, n_viewport, n_window, n_buffer):
        self.n_net = n_net
        self.n_viewport = n_viewport
        self.n_window = n_window
        self.n_buffer = n_buffer

        self.current_width = self.n_buffer.buffer_width
        self.current_height = self.n_buffer.buffer_height

        self.entity = EntityV2()

        self.should_update_entity2 = False

        self.enable_blending = True
        self.dragged = False

        self.force_update = False

    def destroy(self):
        self.entity.destroy()

    def update_scene(self):
        current_frame = self.n_viewport.frame_producer.get_current_frame()
        if current_frame is None:
            print("current frame none")
            return

        current_quad = current_frame.visible_grid_part
        should_update = True

        if self.entity is not None:
            if self.entity.locked:
                return
            if self.entity.visible_grid_part == current_quad:
                should_update = False

        if should_update or self.force_update:
            if not current_frame.ready:
                return
            self.force_update = False
            self.entity.update_entity(current_frame, self.current_width, self.current_height)

            print("update entity",
                  "current factor", self.entity.current_texture_factor)

    def draw_textures(self, n_color_map_v2_texture_shader, alpha_factor):
        n_color_map_v2_texture_shader.use()
        n_color_map_v2_texture_shader.select_texture(self.entity.active_texture_index)
        n_color_map_v2_texture_shader.mix_textures(self.entity.get_fade_progress())
        n_color_map_v2_texture_shader.update_fading_factor(alpha_factor)
        self.entity.draw_texture()

    def draw_points(self, n_instances_from_texture_shader, size):
        n_instances_from_texture_shader.use()
        n_instances_from_texture_shader.update_texture_width(self.current_width)
        n_instances_from_texture_shader.update_texture_height(self.current_height)
        n_instances_from_texture_shader.update_target_width(self.entity.visible_grid_part.w)
        n_instances_from_texture_shader.update_target_height(self.entity.visible_grid_part.h)
        n_instances_from_texture_shader.update_details_factor(self.entity.visible_grid_part.factor)
        n_instances_from_texture_shader.update_position_offset(self.entity.visible_grid_part.offset_x,
                                                               self.entity.visible_grid_part.offset_y)

        n_instances_from_texture_shader.select_texture(0)
        self.entity.draw_points(size)

    def draw_billboards(self, n_billboards_from_texture_shader, size):
        n_billboards_from_texture_shader.use()
        n_billboards_from_texture_shader.update_texture_width(self.current_width)
        n_billboards_from_texture_shader.update_texture_height(self.current_height)
        n_billboards_from_texture_shader.update_target_width(self.entity.visible_grid_part.w)
        n_billboards_from_texture_shader.update_target_height(self.entity.visible_grid_part.h)
        n_billboards_from_texture_shader.update_details_factor(self.entity.visible_grid_part.factor)
        n_billboards_from_texture_shader.update_position_offset(self.entity.visible_grid_part.offset_x,
                                                                self.entity.visible_grid_part.offset_y)
        n_billboards_from_texture_shader.select_texture(self.entity.active_texture_index)
        self.entity.draw_billboards(size, 1)

    def was_buffer_updated(self):
        return self.current_width != self.n_buffer.buffer_width or self.current_height != self.n_buffer.buffer_height

    def draw_scene(self,
                   n_color_map_v2_texture_shader,
                   n_billboards_from_texture_shader
                   ):

        if not self.entity.created or self.was_buffer_updated():
            self.current_width = self.n_buffer.buffer_width
            self.current_height = self.n_buffer.buffer_height
            self.entity.create_data_container_texture(
                self.current_width,
                self.current_height
            )
            self.entity.quad.create_quad()

        # self.flush_buffer()
        self.update_scene()

        max_points_count = 1500000
        max_nodes_count = 500000

        if self.entity.visible_grid_part is None:
            return

        size = self.entity.visible_grid_part.w * self.entity.visible_grid_part.h

        if self.n_viewport.current_factor_half_delta < 1:
            self.draw_billboards(n_billboards_from_texture_shader, size)

        self.draw_textures(n_color_map_v2_texture_shader, self.n_viewport.current_factor_half_delta)
