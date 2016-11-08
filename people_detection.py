import numpy as np
import imutils
import cv2


class PeopleDetection(object):

    def __init__(self, background_path, image_mask=False):
        self.background_cv2 = cv2.imread(background_path)
        self.work_background = imutils.resize(self.background_cv2, width=min(600, self.background_cv2.shape[1]))
        self.background_gray = cv2.cvtColor(self.work_background, cv2.COLOR_BGR2GRAY)
        self.background_gray = cv2.medianBlur(self.background_gray, 5)
        if image_mask:
            self.image_mask = imutils.resize(cv2.imread(image_mask, cv2.IMREAD_GRAYSCALE), width=min(600, self.background_cv2.shape[1]))
        else:
            self.image_mask = False

    def set_background(self, frame, background_path):
        self.background_cv2 = frame
        self.work_background = imutils.resize(self.background_cv2, width=min(600, self.background_cv2.shape[1]))
        cv2.imwrite(background_path, self.work_background)
        self.background_gray = cv2.cvtColor(self.work_background, cv2.COLOR_BGR2GRAY)
        self.background_gray = cv2.medianBlur(self.background_gray, 5)

    def get_background_frame_delta(self, frame):
        frame = imutils.resize(frame, width=(min(600, self.background_cv2.shape[1])))
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame_gray = cv2.medianBlur(frame_gray, 5)
        frame_delta = cv2.absdiff(self.background_gray, frame_gray)
        if self.image_mask is not False:
            frame_delta = cv2.bitwise_and(frame_delta, self.image_mask)
        return frame_delta

    def get_image_thresh(self, frame):
        frame_delta = self.get_background_frame_delta(frame)
        thresh = cv2.threshold(frame_delta, 20, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)
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

    def compute_percent_occupation(self, frame, min_area=350):
        """Compute the occupation percentage of the image."""
        img_size = self.background_gray.size
        frame = imutils.resize(frame, width=(min(600, self.background_cv2.shape[1])))
        contours = self.detect_objects_on_frame(frame)
        total_contour_area = 0.0

        for contour in contours:
            area = cv2.contourArea(contour)
            if area > min_area:
                _, _, w, h = cv2.boundingRect(contour)
                total_contour_area += (w * h)
        if total_contour_area > 0:
            return ((total_contour_area / img_size) * 100)
        else:
            return 0

    def debug_process(self, frame, filepath, min_area=350):
        frame = imutils.resize(frame, width=(min(600, self.background_cv2.shape[1])))
        cv2.imwrite("%s-Orig.jpg" % filepath, frame)
        cv2.imwrite("%s-Thresh.jpg" % filepath, self.get_image_thresh(frame))
        cv2.imwrite("%s-Delta.jpg" % filepath, self.get_background_frame_delta(frame))
        cv2.imwrite("%s-Objects.jpg" % filepath, self.trace_contours(frame.copy(), self.detect_objects_on_frame(frame), min_area))

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
