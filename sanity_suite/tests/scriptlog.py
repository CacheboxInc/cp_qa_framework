import os
import datetime
import logging
import sys
import inspect

def getlogger(foldername):
    # getting the called scriptname
    (frame, scriptname, line_number,
    function_name, lines, index) = inspect.getouterframes(inspect.currentframe())[1]
    if not os.path.exists(foldername):
        os.system('mkdir {0}'.format(foldername))
    logfile = "%s.log" % os.path.join(foldername, scriptname.split('.')[0])
    logger = logging.getLogger('pioqa_cp')
    logger.setLevel(logging.DEBUG)
    
    fh = logging.FileHandler(logfile)
    fh.setLevel(logging.DEBUG)
    
    ch = logging.StreamHandler(sys.__stdout__)
    ch.setLevel(logging.INFO)
    
    fh2 = logging.FileHandler('results.log')
    fh2.setLevel(logging.INFO)
    
    eh = logging.StreamHandler(sys.__stderr__)
    eh.setLevel(logging.WARN)
    
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    eh.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(eh)
        
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    
    fh2.setFormatter(formatter)
    logger.addHandler(fh2)
    
    return logger
