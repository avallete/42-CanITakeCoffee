from cv2 import imwrite
from people_detection import PeopleDetection
from scam import Scam
from time import time

class CameraMonitor(object):

    def __init__(self, camera):
        if not isinstance(camera, Scam):
            raise Exception("Error, camera must be an Scam instance.")
        self.camera = camera
        self.mask = self.camera._get_background_mask_path()
        self.percentage_list = []
        if not self.camera._get_background_img_path():
            imwrite(self.camera._get_background_img_path(), self.camera.get_cam_image())
        self.detector = PeopleDetection(self.camera._get_background_img_path(), self.camera._get_background_mask_path())

    @staticmethod
    def approx_equal(left, right, tolerance=2):
        """Check is (left) is equal to (right) with tolerance."""
        if (abs(left - right) > tolerance):
            return False
        return True

    def get_occupation_percentage(self, min_area=500, debug=False, reset_gap=350):
        """Return the occupation percentage of monitored camera. And take care to update the background image."""
        img = PeopleDetection.pil_to_cv2_img(self.camera.get_cam_image())

        if debug:
            self.detector.debug_process(img, "debug/%s" % int(time()), min_area)
        percent = self.detector.compute_percent_occupation(img, min_area)

        # Check if the image remain approximately the same for enough time to be save as new background.
        if self.percentage_list:
            if self.approx_equal(self.percentage_list[0], percent, 3):
                self.percentage_list.append(percent)
            else:
                self.percentage_list = []
        else:
            self.percentage_list.append(percent)
        if len(self.percentage_list) >= reset_gap:
            self.detector.set_background(img, cam._get_background_img_path())
            self.percentage_list = []

        return percent
