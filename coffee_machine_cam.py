from scam import Scam
from PIL import Image
from io import BytesIO


class CoffeeMachineCam(Scam):

    def __init__(self):
        super(CoffeeMachineCam, self).__init__('cam-kfet-cuisine-se')

    @staticmethod
    def _get_and_crop_data_to_image(data):
        """Take Cam binary data and crop it to remove Date/Hour. And take only coffee machine part of image.
        Then return an Pillow Image object."""
        img = Image.open(BytesIO(data))
        w, h = img.size
        try:
            img.crop((0, 35, 600, (h - 35)))
        except OSError:
            # Every image from scam always raise an 'image file is truncated' error.
            # This first try catch this weird error. TODO (do it properly !)
            pass
        return img.crop((0, 35, 600, (h - 35)))
