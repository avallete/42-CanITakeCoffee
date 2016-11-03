from time import sleep
from scam import Scam
cam = Scam('cam-kfet-cuisine-se')

cam.save_debug_video()
cam.analyse_debug()