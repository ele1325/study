import pytest
from gdcn import *
from expect import *
from image import *
import time

def test_get_display_id():
    result = get_display_id()
    expected = display_id
    assert result == expected

def test_sensor_ident_lesen():
    result = sensor_ident_lesen()
    expected = ident_lesen
    assert result == expected

def test_set_test_image_display_red():
    set_test_image_display(True, 1)
    photo_path = "./photo/red.jpg"
    take_photo(photo_path)
    expected = is_center_color(photo_path, 'red')
    assert expected == True

def test_set_test_image_display_green():
    set_test_image_display(True, 2)
    photo_path = "./photo/green.jpg"
    take_photo(photo_path)
    expected = is_center_color(photo_path, 'green')
    assert expected == True

def test_set_test_image_display_blue():
    set_test_image_display(True, 3)
    photo_path = "./photo/blue.jpg"
    take_photo(photo_path)
    expected = is_center_color(photo_path, 'blue')
    assert expected == True

# def test_set_test_image_display_bmw():
#     set_test_image_display(True, 4)
#     photo_path = "./photo/bmw.jpg"
#     take_photo(photo_path)
#     expected = is_bmw_text(photo_path)
#     assert expected == True