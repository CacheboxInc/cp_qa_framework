# coding=utf-8
"""login feature tests."""

from pytest_bdd import (
    given,
    scenario,
    then,
    when,)
import time

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

global driver

@scenario('login.feature', 'Login with valid credentials')
def test_login_with_valid_credentials():
    """Login with valid credentials."""


@given('Click on login button')
def click_on_login_button():
    print("Click on login button")
    global driver
    driver.find_element_by_xpath(".//button[contains(text(),'Login')]").click()


@given('Enter valid password')
def enter_valid_password():
    print("Enter valid password")
    global driver
    password = driver.find_element_by_id("password")
    password.send_keys("admin@123")

@given('Navigate to appliance')
def navigate_to_appliance_():
    global driver
    #driver = webdriver.Chrome('/home/drugesh/Downloads/chromedriver')
    #driver.WebDriver(command_executor="http://192.168.7.125:4444/wd/hub",desired_capabilities=None, browser_profile='Chrome', proxy=None,keep_alive=False, file_detector=None)
    print("Navigate to appliance")
    driver = webdriver.Remote(command_executor='http://192.168.7.125:4444/wd/hub', desired_capabilities=DesiredCapabilities.CHROME)
    driver.get("https://10.10.14.67/#/login")
    print(driver.title)


@then('Login successful and home page is displayed')
def login_successful_and_home_page_is_displayed():
    print("Login successful and home page is displayed.")
    home = driver.find_element_by_xpath("//img[@alt ='PIO Appliance']")
    #assert driver.title == "PIO Appliance"
    time.sleep(20)
    assert driver.current_url == "https://10.10.117.88/#/plugins"
    driver.close()



@scenario('login.feature', 'Login with invalid credentials')
def test_login_with_invalid_credentials():
        """Login with invalid credentials."""


@given('Enter invalid password')
def enter_invalid_password():
    print("Enter valid password")
    global driver
    password = driver.find_element_by_id("password")
    password.send_keys("admin@1234")

