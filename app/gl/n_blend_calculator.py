class NBlendCalculator:
    def __init__(self):
        # Track levels visibility
        self.levels_visibility = {}
        self.current_delta = 0
        self.min_zoom_level = 0
        self.last_prev = 0
        self.switched = False

    def get_second_texture_mix_factor(self, current_level, prev_level, delta, reached_min_zoom, dragged):

        # print("is outisde",is_outside)
        # switched = False
        # if current_level == self.last_prev:
        #     switched = True
        #
        # self.last_prev = prev_level

        # #came from top
        # if switched:
        #     prev_visibility = 0
        # self.levels_visibility[current_level] = 1-delta
        # empty_prev_level = prev_level is None or prev_level not in self.levels_visibility
        # prev_level_scrolled = 0 if empty_prev_level else round(self.levels_visibility[prev_level])
        # if prev_level_scrolled == 0:
        #     prev_visibility = 0
        # el

        # if prev_level is not None and prev_level > current_level:
        #     prev_visibility = delta
        # else:
        #
        #     prev_visibility = 1-delta
        #
        # self.levels_visibility[current_level] = 1-prev_visibility
        #
        # empty_prev_level = prev_level is None or prev_level not in self.levels_visibility
        # previous_level_visibility = 0 if empty_prev_level else self.levels_visibility[prev_level]
        #
        # if self.current_delta != delta:
        #     print(current_level, prev_level,
        #            previous_level_visibility)
        #     self.current_delta = delta
        # return prev_visibility
        # came from bottom

        #

        if reached_min_zoom:
            self.min_zoom_level = current_level
        empty_prev_level = prev_level is None or prev_level not in self.levels_visibility
        previous_level_visibility = 0 if empty_prev_level else round(self.levels_visibility[prev_level])
        if prev_level == self.min_zoom_level:
            previous_level_visibility = 1

        if dragged:
            current_level_visibility = 1
        elif previous_level_visibility == 0:
            current_level_visibility = 1
        elif current_level < prev_level:
            current_level_visibility = 1 - delta
        else:
            current_level_visibility = delta

        self.levels_visibility[current_level] = current_level_visibility

        if self.current_delta != delta:
            print(current_level, prev_level,
                  "current mix:", current_level_visibility,
                  "prev last:", previous_level_visibility, dragged)
            self.current_delta = delta

        if previous_level_visibility == 0:
            return 0
        else:
            return 1 - current_level_visibility
