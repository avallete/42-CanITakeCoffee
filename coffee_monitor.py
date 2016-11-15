import os
import argparse
import rumps
from blessings import Terminal
from cv2 import imread, imwrite
from coffee_machine_cam import CoffeeMachineCam
from people_detection import PeopleDetection
from camera_monitor import CameraMonitor
from time import sleep

rumps.debug_mode(True)



class SystemTrayMonitor(rumps.App):

    def __init__(self, min_area=500, debug=False):
        super(SystemTrayMonitor, self).__init__("Coffee Machine")
        self.cam = CoffeeMachineCam()
        self.monitor = CameraMonitor(self.cam)
        self.min_area = min_area
        self.debug = debug

    @rumps.timer(1)
    def update_title(self, sender):
        try:
            print(self)
            self.title = "Coffee Machine: %s%%" % int(self.monitor.get_occupation_percentage(self.min_area, self.debug))
        except Exception as e:
            print(e)
            pass
        print("update")

def monitor_print_terminal():
    term = Terminal()

    try:
        with term.fullscreen():
            while True:
                name, percent = (yield)
                with term.location(0, 0):
                    if int(percent) > 0:
                        print("{t.clear}The {cam_name} is: {t.red}{t.bold}occupied ({percent})%{t.normal}.".format(t=term, percent=int(percent), cam_name=name))
                    else:
                        print("{t.clear}The {cam_name} is: {t.green}{t.bold}free{t.normal}.".format(t=term, cam_name=name))
    except GeneratorExit:
        print("Stop monitor, good bye.")

def monitor_coffee_machine(min_area=500, debug=False):
    printer = monitor_print_terminal()
    cam = CoffeeMachineCam()
    monitor = CameraMonitor(cam)
    next(printer)
    try:
        while True:
            percentage = monitor.get_occupation_percentage(min_area, debug)
            printer.send(("Coffee Machine", percentage))
            sleep(1)
    except KeyboardInterrupt:
        printer.close()
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
        detector.set_background(img)
        i += 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--min_area", help="Set the minimum area size for object detection." , type=int, dest="area", default=250)
    parser.add_argument("-d", "--debug", help="""Save each video frame into a debug folder with different debug data.
    *-Orig.jpg: The original image.
    *-Delta.jpg: The delta between current frame and background image.
    *-Thresh.jpg: The Thresh result on image (basically delta with accentuation).
    *-Objects.jpg: Frame with the objects with size > to min_area detected on image.
    """, action="store_true", dest="debug", default=False)
    parser.add_argument("-a", "--analyse", help="""The in parameter the path of a file containing cam screenshoot folder.
    Then, run the debug on it and save result in '/debug/analyse' folder.""", dest="analyse", type=str, default=False)
    parser.add_argument("-r", "--reamon", help="""The in parameter the path of a file containing cam screenshoot folder.
    Then, run the debug on it and save result in '/debug/analyse' folder.""", dest="reamon", type=str, default=False)

    args = parser.parse_args()

    if args.reamon:
        app = SystemTrayMonitor(args.area, args.debug)
        app.run()

    if args.analyse:
        if os.path.exists(args.analyse):
            analyse_folder(args.analyse, args.area)
        else:
            print("Error, %s folder does not exist." % args.analyse)
    else:
        monitor_coffee_machine(args.area, args.debug)
