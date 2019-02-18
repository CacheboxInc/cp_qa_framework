from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import os
import time
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


print(os.getcwd())
from perf_suite.conf_tcs.config import *


host = "10.10.20.24"

url = "https://%s/ui" %(VCENTER_IP)
result = {}



print("Running set up")
driver = webdriver.Remote(command_executor='http://10.10.20.24:4445/wd/hub', desired_capabilities=DesiredCapabilities.CHROME)
driver.maximize_window()
driver.implicitly_wait(2)
wait = WebDriverWait(driver, 420)

def test_1_login_to_vcenter():
   print(url)
   driver.get(url)
   driver.find_element_by_id("username").send_keys(USERNAME)
   driver.find_element_by_id("password").send_keys(PASSWORD)
   driver.find_element_by_id("submit").click()


def test_2_navigate_to_dashboard():
   driver.find_element_by_xpath("//div[contains(@class,'branding')]/a").click()
   time.sleep(1)
   driver.find_element_by_xpath("//div[contains(@class,'branding')]/a").click()
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


   
def test_3_navigate_to_profiling_tab():
   print("Checking for Profiling Page .....")
   driver.switch_to.frame(driver.find_element_by_class_name("sandbox-iframe"))
   driver.find_element_by_xpath("//button[contains(. ,'Profiling')]").click()
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

def test_4_navigate_to_planning_tab():
   print("Checking for planing Page .....")
   driver.switch_to.frame(driver.find_element_by_class_name("sandbox-iframe"))
   driver.find_element_by_xpath("//button[contains(. ,'Cloud Burst')]").click()
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

def test_5_navigate_to_deployment_tab():
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
   
def test_6_navigate_to_monitoring_tab():
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



def test_7_navigate_to_configuration_tab():
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



def test_8_navigate_to_cloud_tab():
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


def test_9_navigate_to_policies_tab():
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
   print("Global Policies tab loading time : %0.2f secs" %(total_time))
   result.update({"Global Policies Page" : "%0.2f secs" %(total_time) })
   driver.switch_to.default_content()


'''def test_10_navigate_to_license_tab():
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



def test_11_navigate_to_about_tab():
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
   driver.switch_to.default_content()'''

def test_10_navigate_cluster_cloud_burst_planning():
   print("Checking for cluster_cloud_burst Page .....")
   driver.find_element_by_xpath("//div[contains(@class,'branding')]/a").click()
   time.sleep(1)
   driver.find_element_by_xpath("//div[contains(@class,'branding')]/a").click()
   time.sleep(3)
   driver.find_element_by_xpath("//a[contains(. ,'Hosts and Clusters')]").click()
   time.sleep(2)
   datacenter = "//span[. ='%s']/parent::div/span[@class = 'k-icon k-plus']"%(DATACENTER)
   driver.find_element_by_xpath(datacenter).click()
   time.sleep(2)
   cluster = "//span[. ='%s']"%(CLUSTER)
   driver.find_element_by_xpath(cluster).click()
   time.sleep(1)
   driver.find_element_by_xpath("//a[contains(. ,'Configure')]").click()
   time.sleep(1)
   driver.find_element_by_xpath("//a[contains(. ,'PrimaryIO')]").click()
   driver.switch_to.frame(driver.find_element_by_class_name("sandbox-iframe"))
   start_time = time.time()
   print("waiting for content to load")
   #waiting for spinner to appear and disappear
   wait.until(EC.visibility_of_element_located((By.XPATH , "//div[contains(@class ,'spinner')]")))
   wait.until(EC.invisibility_of_element_located((By.XPATH , "//div[contains(@class ,'spinner')]")))
   stop_time = time.time()
   total_time = stop_time - start_time
   print("Cloudburst Planning tab loading time : %0.2f secs" %(total_time))
   result.update({"Cluster_cloudburst_planning" : "%0.2f secs" %(total_time) })
   driver.switch_to.default_content()

def test_11_navigate_cluster_administrator_policy():
   print("Checking for cluster_cloud_burst Page .....")
   driver.switch_to.frame(driver.find_element_by_class_name("sandbox-iframe"))
   driver.find_element_by_xpath("//button[contains(. ,'Administration')]").click()
   start_time = time.time()
   print("waiting for content to load")
   #waiting for spinner to appear and disappear
   wait.until(EC.visibility_of_element_located((By.XPATH , "//div[contains(@class ,'spinner')]")))
   wait.until(EC.invisibility_of_element_located((By.XPATH , "//div[contains(@class ,'spinner')]")))
   stop_time = time.time()
   total_time = stop_time - start_time
   print("Cluster  policy tab loading time : %0.2f secs" %(total_time))
   result.update({"Cluster Policies Page" : "%0.2f secs" %(total_time) })
   driver.switch_to.default_content()


def test_12_navigate_cluster_profiling():
   print("Checking for cluster_cloud_burst Page .....")
   driver.find_element_by_xpath("//a[contains(. ,'Monitor')]").click()
   time.sleep(2)
   driver.find_element_by_xpath("//a[contains(. ,'PrimaryIO')]").click()
   driver.switch_to.frame(driver.find_element_by_class_name("sandbox-iframe"))
   start_time = time.time()
   print("waiting for content to load")
   #waiting for spinner to appear and disappear
   wait.until(EC.visibility_of_element_located((By.XPATH , "//div[contains(@class ,'spinner')]")))
   wait.until(EC.invisibility_of_element_located((By.XPATH , "//div[contains(@class ,'spinner')]")))
   stop_time = time.time()
   total_time = stop_time - start_time
   print("Cluster profiling tab loading time : %0.2f secs" %(total_time))
   result.update({"Cluster_Profiling" : "%0.2f secs" %(total_time) })
   driver.switch_to.default_content()

def test_13_navigate_to_cluster_cloudburst_dashboard():
   print("Checking for Cluster Dashboard .....")
   driver.switch_to.frame(driver.find_element_by_class_name("sandbox-iframe"))
   driver.find_element_by_xpath("//button[contains(. ,'Cloud Burst')]").click()
   start_time = time.time()
   print("waiting for content to load")
   #waiting for spinner to appear and disappear
   wait.until(EC.visibility_of_element_located((By.XPATH , "//div[contains(@class ,'spinner')]")))
   wait.until(EC.invisibility_of_element_located((By.XPATH , "//div[contains(@class ,'spinner')]")))
   stop_time = time.time()
   total_time = stop_time - start_time
   print("Cluster Dashboard tab loading time : %0.2f secs" %(total_time))
   result.update({"Cluster_Dashboard" : "%0.2f secs" %(total_time) })
   driver.switch_to.default_content()

def test_14_navigate_to_cluster_deployment():
   print("Checking for Cluster Deployment .....")
   time.sleep(3)
   driver.switch_to.frame(driver.find_element_by_class_name("sandbox-iframe"))
   time.sleep(1)
   driver.find_element_by_xpath("//button[contains(. ,'Deployment')]").click()
   time.sleep(3)
   driver.find_element_by_xpath("//button[contains(. ,'Deployment')]").click()
   start_time = time.time()
   print("waiting for content to load")
   #waiting for spinner to appear and disappear
   wait.until(EC.visibility_of_element_located((By.XPATH , "//div[contains(@class ,'spinner')]")))
   wait.until(EC.invisibility_of_element_located((By.XPATH , "//div[contains(@class ,'spinner')]")))
   stop_time = time.time()
   total_time = stop_time - start_time
   print("Cluster Deployment tab loading time : %0.2f secs" %(total_time))
   result.update({"Cluster_Deployment" : "%0.2f secs" %(total_time) })
   driver.switch_to.default_content()


def test_15_navigate_to_cluster_monitoring():
   print("Checking for Cluster Dashboard .....")
   driver.switch_to.frame(driver.find_element_by_class_name("sandbox-iframe"))
   driver.find_element_by_xpath("//button[contains(. ,'Monitoring')]").click()
   start_time = time.time()
   print("waiting for content to load")
   #waiting for spinner to appear and disappear
   wait.until(EC.visibility_of_element_located((By.XPATH , "//div[contains(@class ,'spinner')]")))
   wait.until(EC.invisibility_of_element_located((By.XPATH , "//div[contains(@class ,'spinner')]")))
   stop_time = time.time()
   total_time = stop_time - start_time
   print("Cluster Monitoring tab loading time : %0.2f secs" %(total_time))
   result.update({"Cluster_Monitoring" : "%0.2f secs" %(total_time) })
   driver.switch_to.default_content()

def test_last_print_summary():
   print("Page Name\tTime")
   for i in result:
      print("{}\t{}".format(i,result[i]))
   print("closing browser")
   driver.quit() 


### Calling the function for noting page load time


"""login_to_vcenter()
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
print_summary()"""
