class NBlendCalculator:
    def __init__(self):
        # Track levels visibility
        self.levels_visibility = {}
        self.current_delta = 0
        self.min_zoom_level = 0
        self.last_prev = 0
        self.switched = False
        self.zooming_in = True

    def get_second_texture_mix_factor(self, current_level, prev_level, delta, reached_min_zoom, dragged):

        # Remember min level
        if reached_min_zoom:
            self.min_zoom_level = current_level

        # The delta goes from 1 to 0 when zooming between levels
        # By default, overlap current level with the previous level and fade out with zoom
        # The previous level can be larger or smaller based on zoom direction
        def default_fun():
            if prev_level is not None and prev_level > current_level:
                prev_mix = delta
            else:
                prev_mix = 1 - delta
            current_mix = 1 - prev_mix
            return prev_mix, current_mix

        # Default setup works well until user changes zoom direction
        # We need to track the level visibility to check if previous level was visible
        # If previous level was not visible, show only the current level
        previous_level_visibility = 0 if prev_level not in self.levels_visibility else round(
            self.levels_visibility[prev_level])

        # If previous level is min level, make sure its always visible
        if prev_level == self.min_zoom_level:
            previous_level_visibility = 1

        # When user dragged the screen, the previous quad doesn't overlap with the current level.
        # Set values to ensure correct result after drag
        if dragged:
            self.levels_visibility[prev_level] = 0
            self.levels_visibility[current_level] = 1
            prev_visibility = 0
            current_visibility = 1

        # If previous level wasn't visible, show only current level
        elif previous_level_visibility == 0:
            prev_visibility = 0
            current_visibility = 1
        else:
            prev_visibility, current_visibility = default_fun()

        self.levels_visibility[current_level] = current_visibility

        # if self.current_delta != delta:
        #     print(current_level, prev_level,
        #           "current vis:", current_visibility,
        #           "prev vis:", prev_visibility,
        #           "drag", dragged)
        #     self.current_delta = delta

        return prev_visibility
