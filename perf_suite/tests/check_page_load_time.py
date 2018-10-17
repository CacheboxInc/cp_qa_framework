from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import os
import time
print(os.getcwd())
#from perf_suite.conf_tcs.config import *

driver = webdriver.Chrome(executable_path=os.getcwd()+'/tools/chromedriver')
driver.maximize_window()
driver.implicitly_wait(2)
vcenter ="10.10.8.58"
url = "https://%s/ui" %(vcenter)
username = "administrator@vsphere.local"
password = "Root@123"
result = {}

wait = WebDriverWait(driver, 100)

def login_to_vcenter():
   print(url)
   driver.get(url)
   driver.find_element_by_id("username").send_keys(username)
   driver.find_element_by_id("password").send_keys(password)
   driver.find_element_by_id("submit").click()


def navigate_to_dashboard():
   driver.find_element_by_id("action-homeMenu").click()
   time.sleep(3)
   print("Checking for Dashboard .....")   
   driver.find_element_by_xpath("//a[contains(.,'PrimaryIO')]").click()
   start_time = time.time()
   driver.switch_to.frame(driver.find_element_by_class_name("sandbox-iframe"))
   #wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(.,'On Premise')]")))
   wait.until(EC.visibility_of_element_located((By.XPATH , "//div/div[2]/div[1]/div/div[2]/div[contains(. , 'Loading')]")))
   wait.until(EC.invisibility_of_element_located((By.XPATH , "//div/div[2]/div[1]/div/div[2]/div[contains(. , 'Loading')]")))
   stop_time = time.time()
   total_time = stop_time - start_time
   print("Dashboard page loading time : %0.2f secs" %(total_time)) 
   result.update({"Dashboard Page" : "%0.2f secs" %(total_time) })
   driver.switch_to.default_content()


   
def navigate_to_cloudburst_tab():
   print("Checking for Cloudburst/Profiling Page .....")
   driver.switch_to.frame(driver.find_element_by_class_name("sandbox-iframe"))
   driver.find_element_by_xpath("//button[contains(. ,'Cloudburst')]").click()
   start_time = time.time()
   #wait.until(EC.visibility_of_element_located((By.CLASS_NAME , "sandbox-iframe")))
   print("waiting for content to load")
   #waiting for spinner to appear and disappear
   wait.until(EC.visibility_of_element_located((By.XPATH , "//div[contains(@class ,'spinner')]")))
   wait.until(EC.invisibility_of_element_located((By.XPATH , "//div[contains(@class ,'spinner')]")))
   stop_time = time.time()
   total_time = stop_time - start_time
   print("Profiling loading time : %0.2f secs" %(total_time))
   result.update({"Profiling Page" : "%0.2f secs" %(total_time) })
   driver.switch_to.default_content()

def navigate_to_palnning_tab():
   print("Checking for planing Page .....")
   driver.switch_to.frame(driver.find_element_by_class_name("sandbox-iframe"))
   driver.find_element_by_xpath("//button[contains(. ,'Planning')]").click()
   start_time = time.time()
   #wait.until(EC.visibility_of_element_located((By.CLASS_NAME , "sandbox-iframe")))
   print("waiting for content to load")
   #waiting for spinner to appear and disappear
   wait.until(EC.visibility_of_element_located((By.XPATH , "//div[contains(@class ,'spinner')]")))
   wait.until(EC.invisibility_of_element_located((By.XPATH , "//div[contains(@class ,'spinner')]")))
   stop_time = time.time()
   total_time = stop_time - start_time
   print("Planning tab loading time : %0.2f secs" %(total_time))
   result.update({"Planning Page" : "%0.2f secs" %(total_time) })
   driver.switch_to.default_content()

def navigate_to_deployment_tab():
   print("Checking for Deployment Page .....")
   driver.switch_to.frame(driver.find_element_by_class_name("sandbox-iframe"))
   driver.find_element_by_xpath("//button[contains(. ,'Deployment')]").click()
   start_time = time.time()
   print("waiting for content to load")
   #waiting for spinner to appear and disappear
   wait.until(EC.visibility_of_element_located((By.XPATH , "//div[contains(@class ,'spinner')]")))
   wait.until(EC.invisibility_of_element_located((By.XPATH , "//div[contains(@class ,'spinner')]")))
   stop_time = time.time()
   total_time = stop_time - start_time
   print("Deployment tab loading time : %0.2f secs" %(total_time))
   result.update({"Deployment Page" : "%0.2f secs" %(total_time) })
   driver.switch_to.default_content()
   
def navigate_to_monitoring_tab():
   print("Checking for Cloudburst Page .....")
   driver.switch_to.frame(driver.find_element_by_class_name("sandbox-iframe"))
   driver.find_element_by_xpath("//button[contains(. ,'Monitoring')]").click()
   start_time = time.time()
   print("waiting for content to load")
   #waiting for spinner to appear and disappear
   wait.until(EC.visibility_of_element_located((By.XPATH , "//div[contains(@class ,'spinner')]")))
   wait.until(EC.invisibility_of_element_located((By.XPATH , "//div[contains(@class ,'spinner')]")))
   stop_time = time.time()
   total_time = stop_time - start_time
   print("MOnitoring tab loading time : %0.2f secs" %(total_time))
   result.update({"Monitoring Page" : "%0.2f secs" %(total_time) })
   driver.switch_to.default_content()



def navigate_to_configuration_tab():
   print("Checking for Configuration Page .....")
   driver.switch_to.frame(driver.find_element_by_class_name("sandbox-iframe"))
   driver.find_element_by_xpath("//button[contains(. ,'Administration')]").click()
   start_time = time.time()
   print("waiting for content to load")
   #waiting for spinner to appear and disappear
   wait.until(EC.visibility_of_element_located((By.XPATH , "//div[contains(@class ,'spinner')]")))
   wait.until(EC.invisibility_of_element_located((By.XPATH , "//div[contains(@class ,'spinner')]")))
   stop_time = time.time()
   total_time = stop_time - start_time
   print("Configuration tab loading time : %0.2f secs" %(total_time))
   result.update({"Configuration Page" : "%0.2f secs" %(total_time) })
   driver.switch_to.default_content()



def navigate_to_cloud_tab():
   print("Checking for Cloud Page .....")
   driver.switch_to.frame(driver.find_element_by_class_name("sandbox-iframe"))
   driver.find_element_by_xpath("//button[contains(. ,'Clouds')]").click()
   start_time = time.time()
   print("waiting for content to load")
   #waiting for spinner to appear and disappear
   wait.until(EC.visibility_of_element_located((By.XPATH , "//div[contains(@class ,'spinner')]")))
   wait.until(EC.invisibility_of_element_located((By.XPATH , "//div[contains(@class ,'spinner')]")))
   stop_time = time.time()
   total_time = stop_time - start_time
   print("Cloud tab loading time : %0.2f secs" %(total_time))
   result.update({"Cloud Page" : "%0.2f secs" %(total_time) })
   driver.switch_to.default_content()


def navigate_to_policies_tab():
   print("Checking for policies Page .....")   
   driver.switch_to.frame(driver.find_element_by_class_name("sandbox-iframe"))
   driver.find_element_by_xpath("//button[contains(. ,'Policies')]").click()
   start_time = time.time()
   print("waiting for content to load")
   #waiting for spinner to appear and disappear
   wait.until(EC.visibility_of_element_located((By.XPATH , "//div[contains(@class ,'spinner')]")))
   wait.until(EC.invisibility_of_element_located((By.XPATH , "//div[contains(@class ,'spinner')]")))
   stop_time = time.time()
   total_time = stop_time - start_time
   print("Plicies tab loading time : %0.2f secs" %(total_time))
   result.update({"Policies Page" : "%0.2f secs" %(total_time) })
   driver.switch_to.default_content()


def navigate_to_license_tab():
   print("Checking for License Page .....")
   driver.switch_to.frame(driver.find_element_by_class_name("sandbox-iframe"))
   driver.find_element_by_xpath("//button[contains(. ,'License')]").click()
   start_time = time.time()
   print("waiting for content to load")
   #waiting for spinner to appear and disappear
   wait.until(EC.visibility_of_element_located((By.XPATH , "//div[contains(@class ,'spinner')]")))
   wait.until(EC.invisibility_of_element_located((By.XPATH , "//div[contains(@class ,'spinner')]")))
   stop_time = time.time()
   total_time = stop_time - start_time
   print("License tab loading time : %0.2f secs" %(total_time))
   result.update({"License Page" : "%0.2f secs" %(total_time) })
   driver.switch_to.default_content()



def navigate_to_about_tab():
   print("Checking for About Page .....")
   driver.switch_to.frame(driver.find_element_by_class_name("sandbox-iframe"))
   driver.find_element_by_xpath("//button[contains(. ,'About')]").click()
   start_time = time.time()
   print("waiting for content to load")
   #waiting for spinner to appear and disappear
   wait.until(EC.visibility_of_element_located((By.XPATH , "//div[contains(@class ,'spinner')]")))
   wait.until(EC.invisibility_of_element_located((By.XPATH , "//div[contains(@class ,'spinner')]")))
   stop_time = time.time()
   total_time = stop_time - start_time
   print("About tab loading time : %0.2f secs" %(total_time))
   result.update({"About Page" : "%0.2f secs" %(total_time) })
   driver.switch_to.default_content()




def tear_down():
   print("closing browser")
   driver.quit()

def print_summary():
   print("Page Name\tTime")
   for i in result:
      print("{}\t{}".format(i,result[i]))

   


### Calling the function for noting page load time


login_to_vcenter()
navigate_to_dashboard()
navigate_to_cloudburst_tab()
navigate_to_palnning_tab()
#navigate_to_deployment_tab()
navigate_to_monitoring_tab()
navigate_to_configuration_tab()
navigate_to_cloud_tab()
navigate_to_policies_tab()
navigate_to_license_tab()
#navigate_to_about_tab()
tear_down()
print_summary()
