import pytest
from assertpy import assert_that
import time

@pytest.mark.jira("CP-1907")
def test_1():
    print ("Printing Value Test 1")
    time.sleep(20)
    assert_that(True).is_true()

@pytest.mark.sanity
def test_2():
    print ("Printing value Test 2")
    time.sleep(20)
    assert True


def test_dummy():
    print("Printing value:  Dummy Test")
    time.sleep(20)
    assert True


