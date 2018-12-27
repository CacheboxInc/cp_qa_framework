from selenium import webdriver
from config import BROWSER
from config import HOST
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from config import APPLIANCE_IP
import os
from ovf_deploy_utils import OVF_Deploy_utils


class WebdriverFactory():
    driverinstance = None

    def initialize_webdriver(self):

        """" configRead = ConfigParser.RawConfigParser()
        print(os.getcwd())
        temp= configRead.read(os.getcwd()+'/common/config.properties')
        browser =configRead.get('basic','browser')"""
        browser = BROWSER
        print("Into Inistailization")
        if browser == 'firefox':
            self.driverinstance = webdriver.Firefox

        elif browser == 'chrome':
            self.driverinstance = webdriver.Chrome("/usr/lib/chromium-browser/chromedriver")
            #self.driverinstance = webdriver.Chrome("/home/drugesh/Downloads/chromedriver")
            #self.driverinstance = webdriver.Chrome()

        elif browser == 'ie':
            self.driverinstance = webdriver.Ie

        elif browser == 'safari':
            self.driverinstance = webdriver.Safari
        elif browser == 'remote':
            #host=configRead.read('basic','host')

            #self.driverinstance = webdriver.Remote(command_executor= HOST+'/wd/hub',desired_capabilities=DesiredCapabilities.CHROME)
            self.driverinstance = webdriver.Remote(command_executor='http://192.168.5.68:4444/wd/hub', desired_capabilities=DesiredCapabilities.CHROME)
            #self.driverinstance = webdriver.Remote(command_executor= HOST+ "/wd/hub",desired_capabilities={"browser_profile" = "Chrome", "proxy"=None})


        else:
            print("Wrong browser passed")

        self.driverinstance.implicitly_wait(5)
        self.driverinstance.maximize_window()
        self.driverinstance.get("http://"+OVF_Deploy_utils().get_ip())
        return self.driverinstance

    def __new__(cls):
        if cls.driverinstance == None:
            cls.driverinstance = cls.initialize_webdriver(cls)

        return cls.driverinstance

    def get_webdriver_instance(self):
        if self.driverinstance is None:
            return self.initialize_webdriver()
        else:
            print("into Else")
            return self.__driverinstance

    def kill_webdriver_instance(self):
        if self.driverinstance is not None:
            self.driverinstance.quit
            self.driverinstance = None






