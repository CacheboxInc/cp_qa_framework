#!/usr/bin/python
# -*- coding: utf-8 -*-
from config import *
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import *
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import logging
from webDriverFactory import WebdriverFactory
import getopt
import sys
import custom_logger as cl
import time
from selenium.webdriver.common.action_chains import ActionChains
import pytest
import os


class BasePage(object):

    log = cl.customLogger(logging.DEBUG)

    def __init__(self, driver):
        # self.driver=WebdriverFactory().get_webdriver_instance()
        # self.driver=WebdriverFactory()
        self.driver = driver
        self.log.info("Into BasePage")

    def screenShot(self, resultMessage):
        """
        Takes screenshot of the current open web page
        """
        fileName = resultMessage + "." + str(round(time.time() * 1000)) + ".png"
        screenshotDirectory = "screenshots/"
        relativeFileName = screenshotDirectory + fileName
        currentDirectory = os.path.dirname(__file__)
        destinationFile = os.path.join(currentDirectory, relativeFileName)
        destinationDirectory = os.path.join(currentDirectory, screenshotDirectory)


        try:
            if not os.path.exists(destinationDirectory):
                os.makedirs(destinationDirectory)
            self.driver.save_screenshot(destinationFile)
            self.log.info("Screenshot save to directory:  " + destinationFile)
        except Exception as e:
            self.log.error("### Exception Occurred when taking screenshot")
            self.log.error ('Error: %s' % e)

    def navigateToAppliance(self):
        try:
            self.driver.maximize_window()
            self.driver.get(APP_LINK)
            self.driver.set_page_load_timeout(TIME_SLEEP)
            self.driver.implicitly_wait(TIME_SLEEP)
        except Exception as e:

            self.log.error ('Error: %s' % e)
        return self.driver

    def login(self, pwd=APPLIANCE_PASSWD):

        if self.elementPresence('password','id'):
            password = self.driver.find_element_by_id('password')
            password.send_keys(pwd)
            self.driver.find_element_by_class_name('btn').click()
            time.sleep(TIME_SLEEP)
            if self.elementPresence('vcenter_heading', 'id'):
                self.log.info("Login Successfull")

            else:
                self.log.error("login Failed")
                return False

    def moving_to_page(self, href):
        self.driver.find_element_by_xpath('//a[@href="' + href + '"]'
                                          ).click()

        return self.driver

    def get_page_header(self, driver_obj):
        ele = self.driver.find_element_by_xpath("//span[@class='col-lg-2']"
                                              ).text

        return ele

    def getByType(self, type):

        if type == 'xpath':
            return By.XPATH
        elif type == 'id':

            return By.ID
        elif type == 'name':

            return By.NAME
        elif type == 'classname':

            return By.CLASS_NAME
        elif type == 'linktext':

            return By.LINK_TEXT
        elif type == 'css' | 'css_selector':

            return By.CSS_SELECTOR
        elif type == 'partiallinktext':

            return By.PARTIAL_LINK_TEXT
        elif type == 'tagname':

            return By.TAG_NAME
        else:

            self.log.info ('Invalid type provided')

    def get_element(self, locator, type='xpath'):
        try:

            element = self.driver.find_element(self.getByType(type),
                                               locator)
            self.log.info ('Found Element ' + locator)
            return element
        except Exception as e:

            self.log.error ('Unable to find Element' + locator)
            self.log.error ('Error: %s' %e)

    def get_elements(self, locator, type='xpath'):
        try:
            elements = self.driver.find_elements(self.getByType(type),
                                                 locator)
            self.log.info ('Found Elements :  ' + locator)
            return elements
        except Exception as e:
            pytest.fail("Unable to find Elements : " + locator)
            self.log.error ('Unable to find Elements : ' + locator)
            self.log.error('Error: %s' % e)

    def click_element(self, locator, type='xpath'):

        element = self.get_element(locator, type)
        self.wait(locator,type)
        try:
            element.click()
            self.log.info ('click Sucessfull locator' + locator)
        except Exception as e:
            self.log.error ('Unable to click on locator: ' + locator)
            self.log.error('Error %s' %e)
            pytest.fail("element not clickable")

    def enter_text(self, data, locator, type='xpath'):
        we = self.get_element(locator, type)
        we.clear()
        we.send_keys(data)
        self.log.info ('Entered data: ' + data + 'in locator' + locator)

    def clear_textfield(self,locator,type):
        we = self.get_element(locator,type)
        try:
            we.clear()
            self.log.info("Cleared text filed")

        except Exception as e:
            self.log.error("Error  : %s" %e )



    def elementPresence(self, locator, type):

        try:
            element = self.driver.find_element(self.getByType(type),
                                               locator)
            if element is not None:
                return True
            else:
                return False
        except Exception as e:
            return False

    def wait(self,locator,type,timeout=10 ):
        try:
            self.log.info ('Waiting for clickable : ' +locator)
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(EC.element_to_be_clickable((self.getByType(type),locator)))
            self.log.info ('Element appeared')
        except Exception as e:
            self.log.error ('Element is not clickable')
            self.log.error(" Error : %s " %e )

    def login(self):
        if not self.elementPresence('vcenters', 'id'):
            self.enter_text('admin@123', "//input[@id='password']")
            self.click_element("//button[text()='Login']")
    
    

    def getSelectOptions(self, locator, type):
        select = Select(self.driver.find_element(self.getByType(type),
                                                 locator))
        options = select.options
        text_options = []
        for opt in options:
            text_options.append(opt.text)
        return text_options

    def navigate_to_page(self, page='dashboard'):
        self.login()
        if page.lower() == 'dashboard':
            self.click_element('dashboard', 'id')
        elif page.lower() == 'vcenters':

            # waiting till page is displayed
            # self.wait("home_heading","id")

            self.click_element('vcenters', 'id')
            #self.wait('vcenterTable', 'id')
        elif page.lower() == 'controlpanel':

            self.click_element('reports', 'id')
            #self.wait('dc-data-table', 'id')


    def element_hover(self, locator, type='xpath'):
        ele = self.get_element(locator, type)
        hover = ActionChains(self.driver).move_to_element(ele)
        hover.click().perform()

    def element_hover(self, element):
        hover = ActionChains(self.driver).move_to_element(element)
        hover.click().perform()

    def logout(self):
        self.click_element("dropdown-toggle", "classname")
        self.click_element("//a[contains(text() ,'Logout')]","xpath")




