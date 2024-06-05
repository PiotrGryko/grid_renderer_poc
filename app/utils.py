import os

import numpy as np
import psutil
from PIL import Image, ImageFont, ImageDraw, ImageOps
from matplotlib import pyplot as plt


class FancyUtilsClass:
    def __init__(self):
        self.process = psutil.Process(os.getpid())
        self.memory_usage = 0
        self.virtual_memory_usage = 0

    def print_memory_usage(self):
        mem_info = self.process.memory_info()
        usage = f"{mem_info.rss / (1024 * 1024 * 1024):.2f}"
        if self.memory_usage != usage:
            self.memory_usage = usage
            print(self.get_memory_message())

    def get_memory_message(self):
        return f"Memory usage: {self.memory_usage} GB"

    def create_logo_message(self):
        w = 600
        h = 600
        base_image = Image.new('L', (w,h), 255)  # 'L' mode for (8-bit pixels, black and white)
        draw = ImageDraw.Draw(base_image)

        logo_image = Image.open('res/logo5.webp').convert('L')
        logo_image = ImageOps.invert(logo_image)
        #webp_image.save('res/logo.png', 'PNG')
        logo_image = ImageOps.flip(logo_image)
        logo_image = logo_image.resize((w,h))
        print("image size",logo_image.width, logo_image.height)

        base_image.paste(logo_image)
        text_array = np.array(base_image)

        print("logo shape",text_array.shape)
        normalized_array = text_array / 255.0
        normalized_array = np.where(normalized_array > 0.5, 1, -1)
        #
        # plt.imshow(normalized_array, cmap='gray')
        # plt.show()
        return normalized_array


    def create_welcome_message(self):
        # Define the grid size
        grid_size = (500, 400)
        gap = 100
        # Calculate the position to center the text
        text_x = 40
        text_y = 100
        show = False

        # Create a blank image with white background
        text_image = Image.new('L', grid_size, 255)  # 'L' mode for (8-bit pixels, black and white)

        # Get a font
        try:
            font = ImageFont.truetype("res/ARIAL.TTF", 80)  # Use a truetype font if available
            print("font loaded")
        except IOError as e:
            font = ImageFont.load_default()
            print("font error ", e)

        try:
            font2 = ImageFont.truetype("res/ARIAL.TTF", 32)  # Use a truetype font if available
            print("font loaded")
        except IOError as e:
            font = ImageFont.load_default()
            print("font error ", e)

        # Create a drawing context
        draw = ImageDraw.Draw(text_image)

        # Define the text and get its size
        text = "MyLittleNet"
        text2 = ("Download the model"
                 "\nor Open the local model"
                 "\n"
                 "\nPress C to change the color")



        # Draw the text
        draw.text((text_x, text_y), text, fill=0, font=font)  # Use fill=0 for black text
        draw.text((text_x, text_y + gap), text2, fill=0, font=font2)  # Use fill=0 for black text

        if not show:
            text_image = ImageOps.flip(text_image)
        # Convert the image to a numpy array
        text_array = np.array(text_image)

        # Normalize the array to be floats between 0 and 1
        normalized_array = text_array / 255.0

        if show:
            # Display the result for verification
            plt.imshow(normalized_array, cmap='gray')
            plt.show()
        return normalized_array
