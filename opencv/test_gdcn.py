import pytest
from gdcn import *
from expect import *
from image import *
import time

def test_status_sw_version():
    if SIL:
        result = [182, 81, 0, 10, 36, 18, 37, 1, 0, 0, 6, 2, 0, 10, 14, 0, 0, 0, 0, 1, 0, 0, 0, 1, 182, 81, 0, 10, 
                  182, 81, 0, 10, 36, 18, 37, 1, 36, 18, 37, 1, 0, 0, 15, 201, 0]
    else:
        result = status_sw_version()
    expected = expected_status_sw_version
    assert result == expected

def test_sensor_ident_lesen():
    if SIL:
        result = [91, 64, 0, 255, 5, 181, 20, 70, 255, 255, 255, 255, 255, 36, 4, 48, 0, 0, 48, 57, 1, 154, 1, 146]
    else:
        result = sensor_ident_lesen()
    expected = expected_sensor_ident_lesen
    assert result[:13] == expected[:13]
    assert result[-4:] == expected[-4:]

def test_get_display_svk():
    if SIL:
        result = [1, 0, 0, 208, 70, 182, 2, 2, 6, 0, 0, 193, 46, 182, 2, 10, 8, 0, 0, 192, 211, 182, 81, 10]
    else:
        result = get_display_svk()
    expected = expected_display_svk
    assert result == expected

def test_get_display_id_short():
    if SIL:
        result = [32, 82, 2, 0, 2, 35]
    else:
        result = get_display_id_short()
    expected = expected_display_id_short
    assert result == expected

def test_get_display_id():
    if SIL:
        result = [32, 82, 2, 0, 32, 2, 12, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 33, 0, 29, 204, 12, 118, 5, 60, 
                  12, 70, 5, 0, 159, 154, 78, 196, 52, 169, 102, 98, 16, 233, 36, 82, 176, 100, 0, 0, 0, 0, 2, 
                  120, 34, 0, 20, 102, 49, 4, 128, 59, 12, 143, 0, 35, 0, 11, 0, 69, 5, 47, 0, 41, 0, 2, 0, 38, 
                  0, 9, 2, 0, 0, 0, 0, 0, 0, 0, 0, 35]
    else:
        result = get_display_id()
    expected = expected_display_id
    assert result == expected

def test_get_dsc_capabilities():
    if SIL:
        result = [1, 33, 1, 9, 1, 1, 0, 3, 6, 0, 24, 0, 0]
    else:
        result = get_dsc_capabilities()
    expected = expected_dsc_capabilities
    assert result == expected

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