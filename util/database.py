from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, Float,String, DateTime, \
     ForeignKey, event, DateTime, ForeignKey
from sqlalchemy.orm import scoped_session, sessionmaker, backref, relation
from sqlalchemy.ext.declarative import declarative_base

# from werkzeug import cached_property, http_date

# from flask import url_for, Markup
# from flask_website import app, search

# engine = create_engine(app.config['DATABASE_URI'],
#                        convert_unicode=True,
#                        **app.config['DATABASE_CONNECT_OPTIONS'])

engine = create_engine('sqlite:///test.db')
db_session = scoped_session(sessionmaker(autocommit=False,
                                        autoflush=False,
                                        bind=engine))

def init_db():
    Model.metadata.create_all(bind=engine)


Model = declarative_base(name='Model')
Model.query = db_session.query_property()


class InitReport(Model):
    __tablename__ = 'initreport'
    id = Column('report_id', Integer, primary_key=True)
    name = Column('name', String(200))
    filename = Column('filename', String(200))
    create_time = Column(DateTime, default=datetime.utcnow)

    def __init__(self, name, filename):
        self.name = name
        self.filename = filename
        # self.create_time = create_time

    def to_json(self):
        return dict(name=self.filename, is_admin=self.is_admin)

    def __eq__(self, other):
        return type(self) is type(other) and self.id == other.id

    def __ne__(self, other):
        return not self.__eq__(other)

class DemoStatus(Model):
    __tablename__ = 'demodulators'

    # 仪表ID
    id = Column('demodulatorID', Integer, primary_key=True)
    # 仪表位置
    position = Column('demodulatorPos', String(200))
    channelnum = Column('channelNum', Integer)
    freq = Column('sampleFreq', Integer)
    onlinetime = Column("onlineDateTime", DateTime, default=datetime.utcnow)
    status = Column("status", String(10))

    def __init__(self, id, position, channelnum, freq, onlinetime, status):
        self.id = id
        self.position = position
        self.channelnum = channelnum
        self.freq = freq
        if isinstance(onlinetime, str):
            self.onlinetime = datetime.strptime(onlinetime, '%Y/%m/%d %H:%M:%S')
        else:
            self.onlinetime = onlinetime
        self.status = status
        # self.create_time = create_time

    def to_json(self):
        return dict(name=self.filename, is_admin=self.is_admin)

    def __eq__(self, other):
        return type(self) is type(other) and self.id == other.id

    def __ne__(self, other):
        return not self.__eq__(other)

class ChannelStatus(Model):
    __tablename__ = 'channels'

    # 通道编号
    number = Column('channelNo', Integer, primary_key=True)
    demoid = Column('demodulatorID', Integer,ForeignKey('demodulators.demodulatorID'), primary_key=True)
    # 仪表位置
    position = Column('channelPos', String(200))
    # channelnum = Column('channelNum', Integer)
    sensornum = Column('sensorNum', Integer)
    framesize = Column("frameSize", Integer)
    packetsize = Column("packetSize", Integer)
    dataflow = Column("dataFlow", Float)
    upgradedate = Column("upgradeDate", DateTime, default=datetime.utcnow)

    def __init__(self, number, demoid, position, sensornum, dataflow,
                 framesize, packetsize, upgradedate):
        self.number = number
        self.demoid = demoid
        self.position = position
        # self.channelnum = channelnum
        self.sensornum = sensornum
        self.framesize = framesize
        self.packetsize = packetsize
        self.upgradedate = upgradedate
        if isinstance(dataflow, float):
            self.dataflow = dataflow
        elif isinstance(dataflow, str):
            dataflow = dataflow.replace("MB/s", "")
            self.dataflow = dataflow
        else:
            self.dataflow = "0.0"
        # self.create_time = create_time

    def to_json(self):
        return dict(name=self.filename, is_admin=self.is_admin)

    def __eq__(self, other):
        return type(self) is type(other) and self.id == other.id

    def __ne__(self, other):
        return not self.__eq__(other)

class Alarms(Model):
    __tablename__ = 'alarms'
    id = Column('id', Integer, primary_key=True)
    level = Column('level', Integer)
    alarmtype = Column("alarmtype", Integer)
    demoid = Column("demoid",  Integer, ForeignKey('demodulators.demodulatorID'))
    channelnum = Column('channelNum', Integer,  ForeignKey('channels.channelNo'))
    # alarminfo 用json字符串存储
    alarminfo = Column("alarminfo", String(2000))
    note = Column("note", String(2000), default="")
    status = Column("status", Integer, default=0)
    create_time = Column(DateTime, default=datetime.utcnow)
    resolve_time = Column(DateTime, default=datetime.utcnow)
    resolve_people = Column(String, default="")

    def __init__(self, level, alarmtype, demoid, channelnum, alarminfo, create_time):   
        self.level = level
        self.alarminfo = alarminfo
        self.alarmtype = alarmtype
        self.channelnum = channelnum
        self.demoid = demoid
        self.alarminfo = alarminfo
        if create_time is not None:
            self.create_time = create_time

    def to_json(self):
        return dict(id=self.id)

    def __eq__(self, other):
        return type(self) is type(other) and self.id == other.id

    def __ne__(self, other):
        return not self.__eq__(other)


def add_report(name, filename):
    global db_session
    irep = InitReport(name, filename)
    db_session.add(irep)
    db_session.commit()

def get_reports():
    reports = InitReport.query.all()
    return reports

def add_demo(id, position, channelnum, freq, onlinetime, status):
    global db_session
    res = DemoStatus.query.filter(DemoStatus.id == id)
    if res.count() > 0:
        # TO update
        print("exisit record")
        res.delete()
   
    demo = DemoStatus(id, position, channelnum, int(freq), onlinetime, status)
    db_session.add(demo)
    db_session.commit()

def add_channel(number, demoid, position, sensornum, dataflow,
                framesize, packetsize, upgradedate):
    global db_session
    res = ChannelStatus.query.filter(ChannelStatus.number == number, ChannelStatus.demoid == demoid)
    if res.count() > 0:
        print("exisit record")
        res.delete()
    
    channel = ChannelStatus(number, demoid, position, sensornum, dataflow,
                            framesize, packetsize, upgradedate)
    db_session.add(channel)
    db_session.commit()

def add_alarm(alrmlevel, alarmtype, demoid,channelnum, alarminfo, create_time):
    print(demoid, alarmtype, alrmlevel)
    alarm = Alarms(alrmlevel, alarmtype, demoid, channelnum, alarminfo,create_time)
    db_session.add(alarm)
    db_session.commit()


def get_demos():
    demos = DemoStatus.query.all()
    return demos

def get_demo(demoid):
    res = DemoStatus.query.filter(DemoStatus.id == demoid)
    if res.count()> 0:
        return res.first()
    else:
        return None

def get_channels(demo_id):
    channels = ChannelStatus.query.filter(ChannelStatus.demoid == demo_id)
    return channels

def get_invasion_alarms():
    invalarms = Alarms.query.filter(Alarms.alarmtype == 1)
    return invalarms.all()

def update_alarm(alarm_id, note, resolve_people):
    alarm = Alarms.query.filter(Alarms.id == alarm_id)
    data_update = {"note":note, "status": 1, "resolve_people": resolve_people}
                #    "resolve_time": datetime.utcnow}
    alarm.update(data_update)
    db_session.commit()

if __name__ == '__main__':
    init_db()
    # print(db_session)
    # add_report(u"初始化报表", "c://aaa.docx")
    # for x in get_reports():
    #     print(x.name, x.filename, x.create_time)
    # add_demo(1, "aaaa", 4, 1000, datetime.now())
    # add_demo(2, "bbb", 4, 1000, datetime.now())
    # add_demo(3, "ccc", 4, 1000, datetime.now())
    # add_channel(1, 1, "aaaa", 4, 100, 100, datetime.now())
    # add_channel(2, 1, "bbbb", 4, 100, 100, datetime.now())
    # add_channel(3, 1, "cccc", 4, 100, 100, datetime.now())
    # demos = get_demos()
    print(get_demo(1))
    # for d in demos:
    #     print(d.position)
    # channels = get_channels(1)
    # for ch in channels:
    #     print(ch.position)