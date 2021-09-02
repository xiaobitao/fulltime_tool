from confluent_kafka import Consumer, KafkaError
import datetime
import pytz
from array import array
import threading
import copy
import time
import json
import random
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

    def __test_v(self):

        tdict = { "datetimeCome": "2020-04-21 14:17:08 763", 
                  "datetimeLeave": "", 
                  "fs": [] ,
                  "sensors": { "buffered": False, "channelNo": 0, "demodulatorID": 0, "groundPos": "",
                  "metroMileage": 0, "metroSection": 0, "regionNo": 0, "sensorNo": 167, "sensorOppNo": 0 },
                  "subwayS": 167, "subwayV": 0, "trainNo": 0 }
        for i in range(200):
            tdict["sensorNo"] = i/2
            tdict["subwayV"] = random.choice(range(30, 60))
            tdict['fs'] = random.sample(range(0, 100), 10)
            # print(tdict)
            self.vechdrive.emit("subwayDemo_subwayInfo", json.dumps(tdict))
            time.sleep(1)

    def __test_alarm(self):
        tdict = { 
                    "alarmLevel": 1, "alarmSensor": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
                    "groundPos": "湖工大侧门" ,
                    "alarmType": "外部入侵",
                    "alarmInfo":[{"alarmSensor": [38, 39, 40, 41, 42], "groundPos": "竹叶山"}, {"alarmSensor": [142, 143, 144, 145, 146], "groundPos": "竹叶山"}, {"alarmSensor": [357, 358, 359, 360, 361], "groundPos": "黄浦路"}],
                    "channels": { "channelNo": 1, "channelPos": "上行道轨", "dataFlow": 2.01, "demodulatorID": 1, "frameSize": 527, "packetSize": 100, "sensorNum": 527 },
                    "sDatetime": "2020-04-27 13:24:46 047" }
        
        # tdict["sensorNo"] = 
        # tdict["subwayV"] = random.choice(range(30, 60))
        # tdict['fs'] = random.sample(range(0, 100), 10)
        # print(tdict)
        # self.invasion.emit("alarmDemo_externalAlarm", json.dumps(tdict))
        time.sleep(10)


    def __init__(self):
        super(KafkaClient, self).__init__()
        # self.c = Consumer({
        #     'bootstrap.servers': '192.168.2.21:9092,192.168.2.20:9092,192.168.2.17:9092',
        #     'group.id': 'mygroup',
        #     'auto.offset.reset': 'earliest'
        # })

        # self.c.subscribe(['topic_initDemo', 'topic_subwayDemo', "topic_externalAlarm"])
        self.working = True

    def run(self):
        while self.working:
            # self.__test_v()
            self.__test_alarm()
            
            

    def process_msg(self, msg):
        # print(msg.topic())
        print("process msg")
        # key = msg.key().decode("utf-8")
        # value = msg.value().decode("utf-8")
        # if msg.topic() == "topic_initDemo":
        #     # self.initmsg.emit(msg.key(), msg.value())
        #     self.initmsg.emit(key, value)
        # elif msg.topic() == "topic_subwayDemo":
        #     self.vechdrive.emit(key, value)
        # elif msg.topic() == "topic_externalAlarm":
        #     print("topic_externalAlarm")
        #     self.invasion.emit(key, value)
    
    def stop(self):
        self.working = False


if __name__ == '__main__':
    # print(get_initmsg())
    kafcli = KafkaClient()
    kafcli.start()
    time.sleep(120)
    
