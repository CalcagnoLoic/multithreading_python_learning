import logging
import time

def thread_function(name):
    logging.info("Thread %s: starting", name)
    time.sleep(10)
    logging.info("Thread %s: finishing", name)