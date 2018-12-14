import http.cookiejar
import copy
import getopt
import inspect
import json
import os
import random
import ssl
import sys
import unittest
import logging
import urllib.request, urllib.parse, urllib.error, urllib.request, urllib.error, urllib.parse
import xmlrpc.client
import pickle
import datetime
from datetime import date
import calendar
import smtplib
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from logging.handlers import TimedRotatingFileHandler



##For logging
log_info = logging.INFO
log_debug = logging.DEBUG
LOG_FILE = "%s/%s.log" % (os.getcwd(), "appliance")
LOG_ROTATION_TIME = 'W2'

formatter1 = logging.Formatter('%(asctime)-15s - %(name)s - %(levelname)s - %(message)s')
formatter2 = logging.Formatter('%(asctime)s - %(name)s - %(message)s')
# logging for profiler
logger = logging.getLogger("pioqa-cp")
logger.setLevel(log_info)
dlr = TimedRotatingFileHandler(LOG_FILE, when=LOG_ROTATION_TIME)
dlr.setLevel(log_info)
dlr.setFormatter(formatter1)
logger.addHandler(dlr)

fh2 = logging.FileHandler('sanity_suite/logs_tcs/result.txt')
fh2.setLevel(log_info)
fh2.setFormatter(formatter2)
logger.addHandler(fh2)



