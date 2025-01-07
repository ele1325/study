import pytest
from gdcn import *
from expect import *
from image import *
import time

# cam = None

def test_init():
    global cam
    cam = open_camera()
    camera_thread = threading.Thread(target=show_camera, args=(cam,))
    camera_thread.start()
    assert cam is not None

def test_set_test_image_display_red():
    global cam    
    set_test_image_display(True, 1)
    photo_path = "./photo/red.jpg"
    take_photo(cam, photo_path)
    expected = is_center_color(photo_path, 'red')
    assert expected == True

def test_set_test_image_display_green():
    global cam
    set_test_image_display(True, 2)
    photo_path = "./photo/green.jpg"
    take_photo(cam, photo_path)
    expected = is_center_color(photo_path, 'green')
    assert expected == True

def test_set_test_image_display_blue():
    global cam
    set_test_image_display(True, 3)
    photo_path = "./photo/blue.jpg"
    take_photo(cam, photo_path)
    expected = is_center_color(photo_path, 'blue')
    assert expected == True

def test_set_test_image_display_bmw():
    global cam
    set_test_image_display(True, 4)
    photo_path = "./photo/bmw.jpg"
    take_photo(cam, photo_path)
    expected = is_bmw_text(photo_path)
    assert expected == True
