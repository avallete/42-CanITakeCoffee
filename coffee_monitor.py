import os
import argparse
from blessings import Terminal
from time import sleep, time
from scam import Scam
from people_detection import PeopleDetection


def monitor_coffee_machine(min_area=500, debug=False):
    cam = Scam('cam-kfet-cuisine-se')
    detector = PeopleDetection(cam._get_background_img_path())
    term = Terminal()
    if debug:
        os.makedirs("debug/", exist_ok=True)
    with term.fullscreen():
        try:
            while True:
                now = int(time())
                img = PeopleDetection.pil_to_cv2_img(cam.get_cam_image())
                if debug:
                    detector.debug_process(img, "debug/%s" % now, min_area)
                occuped = detector.has_people_detected(img, min_area)
                with term.location(0, 0):
                    term.clear_eol()
                    if occuped:
                        print("The coffee machine is: {t.red}{t.bold}occuped{t.normal}.".format(t=term))
                    else:
                        print("The coffee machine is: {t.green}{t.bold}free{t.normal}.".format(t=term))
                sleep(1)
        except KeyboardInterrupt:
            pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--min_area", help="Set the minimum area size for object detection." , type=int, dest="area", default=500)
    parser.add_argument("-d", "--debug", help="""Save each video frame into a debug folder with different debug data.
    *-Delta.jpg: The delta between current frame and background image.
    *-Thresh.jpg: The Thresh result on image (basically delta with accentuation).
    *-Objects.jpg: Frame with the objects with size > to min_area detected on image.
    """, action="store_true", dest="debug", default=False)
    args = parser.parse_args()
    monitor_coffee_machine(args.area, args.debug)