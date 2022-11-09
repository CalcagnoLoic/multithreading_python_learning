import random
import logging
import concurrent.futures
import threading
import time

SENTINEL = object()

def producer(pipeline, event):
    while not event.is_set():
        message = random.randint(1,101)
        logging.info("Producer got message: %s", message)
        pipeline.set_message(message, "Producer")
    
    logging.info("Consumer received EXIT event. Exiting")

def consumer(pipeline, event):
    while not event.is_set() or not pipeline.empty():
        message = pipeline.get_message('Consumer')
        logging.info("Consumer storing message: %s", message, pipeline.qsize())
    
    logging.info("Consumer received EXIT event. Exiting")

class Pipeline:
    def __init__(self) -> None:
        self.message = 0
        self.producer_lock = threading.Lock()
        self.consumer_lock = threading.Lock()
        self.consumer_lock.acquire()

    def get_message(self, name):
        logging.debug("%s: about to acquire getlock", name)
        self.consumer_lock.acquire()
        logging.debug("%s: have getlock", name)
        message = self.message
        logging.debug("%s: about to release setlock", name)
        self.producer_lock.release()
        logging.debug("%s: setlock released", name)
        return message

    def set_message(self, message, name):
        logging.debug("%s: about to acquire setlock", name)
        self.producer_lock.acquire()
        logging.debug("%s: have setlock", name)
        self.message = message
        logging.debug("%s: about to release getlock", name)
        self.consumer_lock.release()
        logging.debug("%s: etlock released", name)

if __name__ == "__main__":
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")
    # logging.getLogger().setLevel(logging.DEBUG)

    pipeline = Pipeline()
    event = threading.Event()
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        executor.submit(producer, pipeline, event)
        executor.submit(consumer, pipeline, event)

        time.sleep(0.1)
        logging.info("Main: about to set event")
        event.set()