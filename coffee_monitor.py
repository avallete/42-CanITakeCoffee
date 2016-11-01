from blessings import Terminal
from time import sleep
from scam import Scam
from people_detection import PeopleDetection


def monitor_coffee_machine():
    cam = Scam('cam-kfet-cuisine-se')
    detector = PeopleDetection(cam._get_background_img_path())
    term = Terminal()
    with term.fullscreen():
        try:
            while True:
                occuped = detector.has_people_detected(PeopleDetection.pil_to_cv2_img(cam.get_cam_image()))
                with term.location(0, 0):
                    if occuped:
                        print("The coffee machine is: {t.red}{t.bold}occuped{t.normal}.".format(t=term))
                    else:
                        print("The coffee machine is: {t.green}{t.bold}free{t.normal}.".format(t=term))
                sleep(1)
        except KeyboardInterrupt:
            pass

if __name__ == "__main__":
    monitor_coffee_machine()