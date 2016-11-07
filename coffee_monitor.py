import os
import argparse
from blessings import Terminal
from cv2 import imread
from coffee_machine_cam import CoffeeMachineCam
from people_detection import PeopleDetection
from time import sleep, time


def monitor_coffee_machine(min_area=500, debug=False):
    cam = CoffeeMachineCam()
    detector = PeopleDetection(cam._get_background_img_path(), "%s/mask.jpg" % cam.dir_path)
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
                percent = detector.compute_percent_occupation(img, min_area)
                with term.location(0, 0):
                    if int(percent) > 0:
                        print("{t.clear}The coffee machine is: {t.red}{t.bold}occupied ({percent})%{t.normal}.".format(t=term, percent=int(percent)))
                    else:
                        print("{t.clear}The coffee machine is: {t.green}{t.bold}free{t.normal}.".format(t=term))
                sleep(1)
        except KeyboardInterrupt:
            pass

def analyse_folder(path, min_area=500):
    cam = CoffeeMachineCam()
    detector = PeopleDetection(cam._get_background_img_path(), "%s/mask.jpg" % cam.dir_path)
    i = 0

    os.makedirs("debug/analyse/", exist_ok=True)
    for filename in os.listdir(path):
        img = imread("%s/%s" % (path, filename))
        print("{i}  :: occupation: {percent}%".format(i=i, percent=int(detector.compute_percent_occupation(img, min_area))))
        detector.debug_process(img, "debug/analyse/%s" % i, min_area)
        i += 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--min_area", help="Set the minimum area size for object detection." , type=int, dest="area", default=1500)
    parser.add_argument("-d", "--debug", help="""Save each video frame into a debug folder with different debug data.
    *-Orig.jpg: The original image.
    *-Delta.jpg: The delta between current frame and background image.
    *-Thresh.jpg: The Thresh result on image (basically delta with accentuation).
    *-Objects.jpg: Frame with the objects with size > to min_area detected on image.
    """, action="store_true", dest="debug", default=False)
    parser.add_argument("-a", "--analyse", help="""The in parameter the path of a file containing cam screenshoot folder.
    Then, run the debug on it and save result in '/debug/analyse' folder.""", dest="analyse", type=str, default=False)
    args = parser.parse_args()
    if args.analyse:
        if os.path.exists(args.analyse):
            analyse_folder(args.analyse, args.area)
        else:
            print("Error, %s folder does not exist." % args.analyse)
    else:
        monitor_coffee_machine(args.area, args.debug)
