import requests
import os

from people_detection import PeopleDetection
from PIL import Image
from io import BytesIO
from time import time, sleep


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

    def __init__(self, camera):
        """Return the Scam object for the camera."""
        self.region = self._get_camera_region(camera)
        self.camera = camera
        self.dir_path = "img/%s/%s" % (self.region, self.camera)
        self.pd = PeopleDetection(self._get_background_img_path())

    def _get_camera_region(self, camera):
        """Get the region of the camera. Return the region if camera is found. Else raise CamDoesNotExist exception."""
        for cam_region, cam_list in self.cam_endpoints.items():
            if camera in cam_list:
                return cam_region
        raise self.CamDoesNotExist("???", camera)

    def _get_cam_data(self, camera):
        """
        Perform an GET request to scam and return the camera image as binary content if success.
        If request fail, return None.
        """
        nowstamp = int(time())
        try:
            rep = requests.get("%s%s?%s" % (self.base_url, (self.scam_endpoint % camera), nowstamp))
            if rep.ok:
                return rep.content
        except requests.exceptions.RequestException as e:
            print("Error with request: %s" % e)
        return None

    def _get_background_img_path(self):
        """Try to get the background image. Return the path if exist, else return None"""
        if os.path.isfile("%s/background.jpg" % (self.dir_path)):
            return "%s/background.jpg" % (self.dir_path)
        else:
            return None

    @staticmethod
    def _get_and_crop_data_to_image(data):
        """Take Cam binary data and crop it to remove Date/Hour. Then return an Pillow Image object."""
        img = Image.open(BytesIO(data))
        w, h = img.size
        try:
            img.crop((0, 35, w, (h - 35)))
        except OSError:
            # Every image from scam always raise an 'image file is truncated' error.
            # This first try catch this weird error. TODO (do it properly !)
            pass
        return img.crop((0, 35, w, (h - 35)))

    def get_cam_image(self):
        """Return Image object of the camera current image. Else return None"""
        data = self._get_cam_data(self.camera)
        if data:
            return self._get_and_crop_data_to_image(data)
        else:
            return None

    def save_cam_image(self, filename="1.jpg"):
        """
        Save the desired self.camera into the img path: img/{self.region}/{self.camera}/{filename}.
        Return Image object of the current image on camera.
        """
        os.makedirs(self.dir_path, exist_ok=True)
        img = self.get_cam_image()
        img.save("%s/%s" % (self.dir_path, filename), "JPEG")
        return img

    # def save_debug_video(self):
    #     os.makedirs("%s/debug/raw" % self.dir_path, exist_ok=True)
    #     try:
    #         while True:
    #             self.save_cam_image("debug/raw/%s.jpg" % int(time()))
    #             sleep(1)
    #     except KeyboardInterrupt:
    #         pass
    #
    # def analyse_debug(self):
    #     os.makedirs("%s/debug/analysis" % self.dir_path, exist_ok=True)
    #     for filename in os.listdir("%s/debug/raw" % self.dir_path):
    #         img = Image.open("%s/debug/raw/%s" % (self.dir_path, filename))
    #         self.pd.detect_and_show_img(self.pd.pil_to_cv2_img(img), "%s/debug/analysis/%s" % (self.dir_path, filename[:-4]))

    # def show_detection(self):
    #     frame = self.get_cam_image()
    #     self.pd.detect_and_show_img(self.pd.pil_to_cv2_img(frame))
