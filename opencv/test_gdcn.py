import pytest
from gdcn import *
from expect import *
from image import *
import time

def test_sensor_ident_lesen():
    if SIL:
        result = [91, 64, 0, 255, 5, 181, 20, 70, 255, 255, 255, 255, 255, 36, 4, 48, 0, 0, 48, 57, 1, 154, 1, 146]
    else:
        result = sensor_ident_lesen()
    expected = expected_sensor_ident_lesen
    assert result[:13] == expected[:13]
    assert result[-4:] == expected[-4:]

# def test_get_display_svk():
#     if SIL:
#         result = [1, 0, 0, 208, 70, 182, 2, 2, 6, 0, 0, 193, 46, 182, 2, 10, 8, 0, 0, 192, 211, 182, 81, 10]
#     else:
#         result = get_display_svk()
#     expected = expected_display_svk
#     assert result == expected

# def test_get_display_id_short():
#     result = get_display_id_short()
#     expected = expected_display_id
#     assert result == expected

# def test_get_display_id():
#     result = get_display_id()
#     expected = expected_display_id
#     assert result == expected

# def test_set_test_image_display_red():
#     set_test_image_display(True, 1)
#     photo_path = "./photo/red.jpg"
#     take_photo(photo_path)
#     expected = is_center_color(photo_path, 'red')
#     assert expected == True

# def test_set_test_image_display_green():
#     set_test_image_display(True, 2)
#     photo_path = "./photo/green.jpg"
#     take_photo(photo_path)
#     expected = is_center_color(photo_path, 'green')
#     assert expected == True

# def test_set_test_image_display_blue():
#     set_test_image_display(True, 3)
#     photo_path = "./photo/blue.jpg"
#     take_photo(photo_path)
#     expected = is_center_color(photo_path, 'blue')
#     assert expected == True

# def test_set_test_image_display_bmw():
#     set_test_image_display(True, 4)
#     photo_path = "./photo/bmw.jpg"
#     take_photo(photo_path)
#     expected = is_bmw_text(photo_path)
#     assert expected == True