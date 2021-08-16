""" Data Access For Damping Analysis
"""
""" Get data from db
"""

import sqlalchemy as sa
from datetime import datetime
import numpy as np
try:
    from ..util.mysql import engine, metadata
except (ImportError , ValueError) as ve:
    from util.mysql import engine, metadata



damping_evals =  metadata.tables['damping_evals']

channels = metadata.tables['channels']
sensors = metadata.tables['sensors']


def list_channels():
    rs = engine.execute(channels.select())
    channel_rows = rs.fetchall()

    print(channel_rows)

    return channel_rows



def list_damping_trend_for_sensor(channel, sensor, date_range = None, **kwargs):
    """ Individual Sensor based damping values
    """

    stmt = damping_evals.select().where(
            sa.and_(
                damping_evals.c.channelNo == channel.channelNo,
                sa.between(damping_evals.c.evalDate, date_range[0], date_range[1]),
                damping_evals.c.sensorNo == sensor,
            )
        ).order_by(sa.asc(damping_evals.c.evalDate))
    rows = engine.execute(stmt).fetchall()
    print("trend result size:", len(rows))
    if len(rows) > 0:
        print("a sample row:", rows[0])
    
    return rows


def latest_eval_date(channel):
    """ The latest date when the evaluation has bee done.
    """
    stmt = damping_evals.select().where(
            damping_evals.c.channelNo == channel.channelNo
        ).order_by(
            sa.desc(damping_evals.c.evalDate)
        ).limit(1)

    latest_date_row = engine.execute(stmt).fetchone()
    
    if latest_date_row is None:
        return None
    else:
        date_value = latest_date_row.evalDate
        return date_value



def list_damping_evals_for_channel(channel, evalDate = None, latest=False, **kwargs):
    """ 
    channel is a dict (model) or sqlalchemy result row representing channel attributes.

    If evalDate is None, get the latest.
    
    """
    damping_area_only = False
    if kwargs.get('damping_flag'):
        damping_area_only = True
    date_value = evalDate

    if latest:
        # Try to get the lastest first.
        date_value = latest_eval_date(channel)

    criteria = [damping_evals.c.channelNo == channel.channelNo,
                damping_evals.c.evalDate == date_value,
            ]

    if damping_area_only:
        criteria.extend(
        ( damping_evals.c.channelNo == sensors.c.channelNo,
          damping_evals.c.sensorNo == sensors.c.sensorNo,
          sensors.c.isBuffered == True,
        ))

    result = engine.execute(
            damping_evals.select().where(sa.and_(*criteria)) \
                .order_by(damping_evals.c.sensorNo)
            )
    data = result.fetchall()
    
    return date_value, data

def feed_signal_files(filter_=None):
    """ 
    """
    result = engine.execute(damping_evals.select())
    converted_result = list()
    for r in result:
        d = dict(r)
        # handle types that can't be encoded by the default json package.

        spec = [('create_dt', lambda v: v.strftime(core.datetime_format)),
                ('signal_blob', lambda v: np.frombuffer(v, dtype=np.dtype(np.float32)).tolist())
        ]

        for k, f in spec:

            d[k] = f(d[k])

        converted_result.append(d)
    return converted_result
    

def insert_damping(data):

    ins = damping_evals.insert()
    channel_dict = data['channel']

    channelNo = channel_dict['channelNo']
    demodulatorID = channel_dict['demodulatorID']
    sensorNum = channel_dict['sensorNum']
    dampingPara = data['dampingPara']

    rows = list()

    for i in range(sensorNum):
        row = {
            "evalDate": data['date'],
            "demodulatorID": demodulatorID,
            "channelNo": channelNo,
            # TODO: We might need a transformer if sensorNo is defined in some other way.
            "sensorNo": i, 
            "dampingPara": dampingPara[i],

        }
        rows.append(row)

    with engine.begin() as conn:
        conn.execute(ins, *rows)
        




