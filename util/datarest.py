import random
import re
import struct
import numpy as np
import json
from flask import Flask, request, jsonify
from flask import Response

app = Flask(__name__)

NFSMOUNT='/root/mount/'

def read_binfile(filepath):
    param = re.findall(r'\d+', re.findall(r'\d+x\d+', filepath)[0])
    rows = int(param[0])
    cols = int(param[1])
    print(rows, cols)
    with open(filepath, 'rb') as f:
        data = f.read()
        value = struct.unpack(str(rows * cols) + 'f', data)
        records = np.array(value).reshape(rows, cols)
        return records
    return None


@app.route('/')
def hello():
    return "Hello World!"

@app.route('/resource', methods = ['POST'])
def test():
    return "Success"

@app.route('/fileinfo', methods = ['GET'])
def vechpos():
    return Response(json.dumps(random.choice(car_data)), status=200, mimetype='application/json')

# parameter
# filepath  the filepath of hadoop(转换到nfs的路径)
# points the data of point
# 如果数据量大了不行，可以一次限定个数，多次取
# reqest
'''
{
   "file": "/nfs/data/p0/20190702/0-20190715235942622-60000x527.bin"
   "points": [1, 12, 25]
}
'''
# return 
'''
{
    "points": [
        {"number", 1, "data": [0.1, 0.2, ......., 1.0]},
        {"number", 2, "data": [0.1, 0.2, ......., 1.0]},
        {"number", 3, "data": [0.1, 0.2, ......., 1.0]}

    ]
}
'''
@app.route('/data', methods = ['POST'])
def datapoints():
    # param in reqeust
    print("hhhh")
    data = json.loads(request.data)
    print(data)
    print(type(data))
    if 'file' not in data:
        return Response("Not file in reqeust", status=400, mimetype='application/json')
    fl = data["file"]
    fl = fl.replace('/nfs/', NFSMOUNT) 
    recs = read_binfile(fl)
    print(recs.ndim)
    reqpts = data["points"]
    resp_points = []
    for pt in reqpts:
        data = recs[:, pt]
        resp_points.append({"number":str(pt), "data": data.tolist()})
    
       
    return Response(json.dumps({"points": resp_points}), status=200, mimetype='application/json')

    


if __name__ == '__main__':
    app.run(host='0.0.0.0')
