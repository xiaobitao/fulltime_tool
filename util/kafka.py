from confluent_kafka import Consumer, KafkaError
import datetime
import pytz
from array import array
import threading
import copy
import time
from PySide2 import QtCore

topics_callback = {}

def register_topic(topic, callback):
    if topic in topics_callback:
        # to log
        pass
    topics_callback[topic] = callback
    

class KafkaClient(QtCore.QThread):

    initmsg = QtCore.Signal(str, str)
    vechdrive = QtCore.Signal(str, str)
    invasion = QtCore.Signal(str, str)

    def __init__(self):
        super(KafkaClient, self).__init__()
        self.c = Consumer({
            'bootstrap.servers': '192.168.2.21:9092,192.168.2.20:9092,192.168.2.17:9092',
            'group.id': 'mygroup',
            'auto.offset.reset': 'earliest'
        })

        self.c.subscribe(['topic_initDemo', 'topic_subwayDemo', "topic_externalAlarm"])
        self.working = True

    def run(self):
        while self.working:
            msg = self.c.poll(1)
            # print(msg)
            if msg is None:
                continue
            if msg.error():
                # TODO log
                continue
            self.process_msg(msg)

    def process_msg(self, msg):
        # print(msg.topic())
        print("process msg")
        key = msg.key().decode("utf-8")
        value = msg.value().decode("utf-8")
        if msg.topic() == "topic_initDemo":
            # self.initmsg.emit(msg.key(), msg.value())
            self.initmsg.emit(key, value)
        elif msg.topic() == "topic_subwayDemo":
            self.vechdrive.emit(key, value)
        elif msg.topic() == "topic_externalAlarm":
            print("topic_externalAlarm")
            self.invasion.emit(key, value)
    
    def stop(self):
        self.working = False


if __name__ == '__main__':
    # print(get_initmsg())
    kafcli = KafkaClient()
    kafcli.start()
    time.sleep(120)
    
