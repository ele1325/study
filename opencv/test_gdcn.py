import pytest
from gdcn import *
from expect import *

def test_get_display_id():

    result = get_display_id()
    expected = display_id
    assert result == expected