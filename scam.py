import requests
import os

from PIL import Image
from io  import BytesIO
from time import time

from pip._vendor.distlib.metadata import _get_name_and_version


class Scam(object):

    base_url = "http://scam.42.fr"
    cam_endpoints = {
        # region: [camera, camera, camera]
        "e0": [
            "cam-e1-sm-rue",
            "cam-e1-sm-resto",
            "cam-e0-petit-couloir",
        ],
        "e1": [
            "cam-e1-hall-porte",
            "cam-e1-sm-so",
            "cam-e1-sm-se",
            "cam-e1-sm-ne",
            "cam-e1-sm-no",
        ],
        "e2": [
            "cam-e2-playstation",
            "cam-e2-detente-sud",
            "cam-e2-detente-ouest",
            "cam-e2-detente-est",
            "cam-e2-sm-porte",
            "cam-e2-sm-so",
            "cam-e2-sm-se",
            "cam-e2-sm-ne",
            "cam-e2-sm-no",
        ],
        "e3": [
            "cam-e3-sm-porte",
            "cam-e3-sm-so",
            "cam-e3-sm-se",
            "cam-e3-sm-ne",
            "cam-e3-sm-no",
        ],
        "amphi": [
            "cam-e0-amphi-rue",
            "cam-e0-amphi-resto",
        ],
        "bocal": [
            "cam-e3-bocal-out",
        ],
        "kfet": [
            "cam-ext-rie-nord",
            "cam-ext-rie-sud",
            "cam-kfet-cuisine-no",
            "cam-kfet-cuisine-se",
            "cam-kfet-bar-no",
            "cam-kfet-bar-se",
            "cam-kfet-resto-ne",
            "cam-kfet-resto-so",
        ],
        "cloture": [
            "cam-ext-moto",
            "cam-ext-moto2",
            "cam-ext-angle-r-sud",
            "cam-ext-angle-b-est",
            "cam-ext-portillon-nord",
            "cam-ext-portillon-sud",
            "cam-ext-sas-nord",
            "cam-ext-sas-sud",
            "cam-ext-rie-nord",
        ],
    }
    scam_endpoint = "/cams/%s.jpg"


    class CamDoesNotExist(Exception):
        """Only purpose of this exception is to give a clear message error for debug."""
        def __init__(self, region, camera):
            super(CamDoesNotExist, self).__init__("Error camera: %s (%s) does not exist." % (camera, region))

    def _get_cam_data(self, region, camera):
        """
        Perform an GET request to scam and return the camera image as binary content if success.
        If request fail, return None.
        If one or both of parameters are invalid, this function raise an CamDoesNotExist Exception.
        """
        if ((region not in self.cam_endpoints.keys()) or (not camera in self.cam_endpoints[region])):
            raise self.CamDoesNotExist(region, camera)
        else:
            nowstamp = int(time())
            try:
                rep = requests.get("%s%s?%s" % (self.base_url, (self.scam_endpoint % camera), nowstamp))
                if rep.ok:
                    return (rep.content)
            except requests.exceptions.RequestException as e:
                print("Error with request: %s" % e)
            return (None)

    def _get_and_crop_data_to_image(self, data):
        """Take Cam binary data and crop it to remove Date/Hour. Then return an Pillow Image object."""
        img = Image.open(BytesIO(data))
        w, h = img.size
        try:
            img.crop((0, 35, w, (h - 35)))
        except OSError:
            # Every image from scam always raise an 'image file is truncated' error.
            # This first try catch this weird error. TODO (do it properly !)
            pass
        return (img.crop((0, 35, w, (h - 35))))

    def _save_and_crop_data_to_image(self, data, outpath):
        """Take Cam binary data, crop it to remove Date/Hour and save it into an .jpg file."""
        self._get_and_crop_data_to_image(data).save(outpath, "JPEG")

    def save_cam_image(self, region, camera, filename="1.jpg"):
        """
        Save the desired camera into the img path: img/{region}/{camera}/{filename}.
        Return imagepath if success, else return False.
        """
        dir_path = "img/%s/%s" % (region, camera)
        os.makedirs(dir_path, exist_ok=True)
        try:
            data = self._get_cam_data(region, camera)
            if data:
                self._save_and_crop_data_to_image(data, "%s/%s" % (dir_path, filename))
                return ("%s/%s" % (dir_path, filename))
            else:
                print("An error occured with scam website.")
        except (self.CamDoesNotExist) as e:
            print(e)
        return (False)

    def save_cam_sequence(self, region, camera, filename="1.we"):