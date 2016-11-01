from imutils.object_detection import non_max_suppression
from imutils import paths
import numpy as np
import argparse
import imutils
import cv2


class PeopleDetection(object):

    def __init__(self, background_path):
        self.background_cv2 = cv2.imread(background_path)
        self.work_background = imutils.resize(self.background_cv2, width=min(600, self.background_cv2.shape[1]))
        self.background_gray = cv2.cvtColor(self.work_background, cv2.COLOR_BGR2GRAY)
        self.background_gray = cv2.medianBlur(self.background_gray, 5)

    def get_background_frame_delta(self, frame):
        frame = imutils.resize(frame, width=(min(600, self.background_cv2.shape[1])))
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame_gray = cv2.medianBlur(frame_gray, 5)
        frame_delta = cv2.absdiff(self.background_gray, frame_gray)
        return frame_delta

    def get_image_thresh(self, frame):
        frame_delta = self.get_background_frame_delta(frame)
        thresh = cv2.threshold(frame_delta, 35, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=5)
        return thresh

    def detect_objects_on_frame(self, frame):
        """frame parameter must be an valid cv2 frame. Return the rect of peoples detected on image."""
        thresh = self.get_image_thresh(frame)
        _, cnts, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        return cnts

    def has_people_detected(self, frame, min_area=350):
        """Return True if some people are detected on frame. Else return False."""
        frame = imutils.resize(frame, width=(min(600, self.background_cv2.shape[1])))
        contours = self.detect_objects_on_frame(frame)
        for contour in contours:
            if cv2.contourArea(contour) >= min_area:
                return True
        return False

    @staticmethod
    def trace_contours(frame, contours, min_area=350):
        """Trace rect for each countours on frame if the size of countour is greater than min_area. Return frame."""
        for contour in contours:
            if cv2.contourArea(contour) >= min_area:
                (x, y, w, h) = cv2.boundingRect(contour)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        return frame

    @staticmethod
    def pil_to_cv2_img(image):
        """Convert an pil Image object into an cv2 valid Image object."""
        return np.array(image)[:, :, ::-1].copy()
