import random

import numpy as np
from matplotlib import pyplot as plt


class NColorTheme:
    def __init__(self):
        self.index = None
        self.color_array = None
        self.cmap = None
        self.color_low = None
        self.name = None
        self.cmap_options = ['Accent', 'Accent_r', 'Blues', 'Blues_r', 'BrBG', 'BrBG_r', 'BuGn', 'BuGn_r', 'BuPu',
                             'BuPu_r',
                             'CMRmap', 'CMRmap_r', 'Dark2', 'Dark2_r', 'GnBu', 'GnBu_r', 'Greens', 'Greens_r', 'Greys',
                             'Greys_r',
                             'OrRd', 'OrRd_r', 'Oranges', 'Oranges_r', 'PRGn', 'PRGn_r', 'Paired', 'Paired_r',
                             'Pastel1',
                             'Pastel1_r', 'Pastel2', 'Pastel2_r', 'PiYG', 'PiYG_r', 'PuBu', 'PuBuGn', 'PuBuGn_r',
                             'PuBu_r', 'PuOr',
                             'PuOr_r', 'PuRd', 'PuRd_r', 'Purples', 'Purples_r', 'RdBu', 'RdBu_r', 'RdGy', 'RdGy_r',
                             'RdPu',
                             'RdPu_r', 'RdYlBu', 'RdYlBu_r', 'RdYlGn', 'RdYlGn_r', 'Reds', 'Reds_r', 'Set1', 'Set1_r',
                             'Set2',
                             'Set2_r', 'Set3', 'Set3_r', 'Spectral', 'summer_r', 'Wistia', 'Wistia_r', 'YlGn', 'YlGnBu',
                             'YlGnBu_r', 'YlGn_r', 'YlOrBr', 'YlOrBr_r', 'YlOrRd', 'YlOrRd_r', 'afmhot', 'afmhot_r',
                             'autumn',
                             'autumn_r', 'binary', 'binary_r', 'bone', 'bone_r', 'brg', 'brg_r', 'bwr', 'bwr_r',
                             'cividis',
                             'cividis_r', 'cool', 'cool_r', 'coolwarm', 'coolwarm_r', 'copper', 'copper_r', 'cubehelix',
                             'cubehelix_r', 'flag', 'flag_r', 'gist_earth', 'gist_earth_r', 'gist_gray', 'gist_gray_r',
                             'gist_heat',
                             'gist_heat_r', 'gist_ncar', 'gist_ncar_r', 'gist_rainbow', 'gist_rainbow_r', 'gist_stern',
                             'gist_stern_r', 'gist_yarg', 'gist_yarg_r', 'gnuplot', 'gnuplot2', 'gnuplot2_r',
                             'gnuplot_r', 'gray',
                             'gray_r', 'hot', 'hot_r', 'hsv', 'hsv_r', 'inferno', 'inferno_r', 'jet', 'jet_r', 'magma',
                             'magma_r',
                             'nipy_spectral', 'nipy_spectral_r', 'ocean', 'ocean_r', 'pink', 'pink_r', 'plasma',
                             'plasma_r',
                             'prism', 'prism_r', 'rainbow', 'rainbow_r', 'seismic', 'seismic_r', 'spring', 'spring_r',
                             'summer',
                             'summer_r', 'tab10', 'tab10_r', 'tab20', 'tab20_r', 'tab20b', 'tab20b_r', 'tab20c',
                             'tab20c_r',
                             'terrain', 'terrain_r', 'turbo', 'turbo_r', 'twilight', 'twilight_r', 'twilight_shifted',
                             'twilight_shifted_r', 'viridis', 'viridis_r', 'winter', 'winter_r']

        self.load_cmap(random.randint(0, len(self.cmap_options)))

    def next(self):
        size = len(self.cmap_options)
        index = (self.index+1) % size
        self.load_cmap(index)
    def load_cmap(self, index):
        index = min(index, len(self.cmap_options)-1)
        self.index = index
        self.name = self.cmap_options[self.index]
        self.cmap = plt.cm.get_cmap(self.name)
        self.color_low = self.cmap(-1)

        num_colors = 255
        values = np.linspace(0, 1, num_colors)  # Generate 255 evenly spaced values between 0 and 1
        self.color_array = self.cmap(values)[:, :3]  # Get the RGB values for these points
        self.color_array = (self.color_array * 255).astype(np.uint8).flatten()  # Convert to 8-bit and flatten

        print("Color option:", self.name)
