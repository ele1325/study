import pytest
from gdcn import *
from expect import *

def test_status_sw_version():
    result = status_sw_version()
    expected = expected_status_sw_version
    assert result[:16] == expected[:16]
    assert result[-5:] == expected[-5:]

def test_sensor_ident_lesen():
    result = sensor_ident_lesen()
    expected = expected_sensor_ident_lesen
    assert result[:13] == expected[:13]
    assert result[-4:] == expected[-4:]

def test_get_display_svk():
    result = get_display_svk()
    expected = expected_display_svk
    assert result == expected

def test_get_display_id_short():
    result = get_display_id_short()
    expected = expected_display_id_short
    assert result == expected

def test_get_display_id():
    result = get_display_id()
    expected = expected_display_id
    assert result == expected

def test_get_dsc_capabilities():
    result = get_dsc_capabilities()
    expected = expected_dsc_capabilities
    assert result == expected