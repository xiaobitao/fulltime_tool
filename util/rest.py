import requests
import json

#TODO host and port to config in config file
host = "192.168.2.21"
port = "5000"
from util.wimlog import error, info, debug


class VechRest():
    def __init__(self):
        pass

    def get_vechpos(self):
        url = "http://%s:%s/vechpos" % (host, port)
        try:
            r = requests.get(url)
            #TODO check result is success
        except Exception as e:
            error(str(e))
            return None
        return r.json()


class InitReport():
    def __init__(self):
        pass

    def get_init_report(self):
        url = "http://%s:%s/initrep" % (host, port)
        try:
            r = requests.get(url)
            #TODO check result is success
        except Exception as e:
            error(str(e))
            return None
        print(r)
        return r.json()

class PointsData(object):
    points = []
    def __init__(self):
        pass

    '''
    points is array of point number
    '''
    def get_points(self, filepath, points):
        payload = {'file': filepath, 'points': points}
        url = "http://%s:%s/data" % (host, port)
        r = requests.post(url, json=payload)
        if r.status_code == 200:
            self.points = r.json()["points"]
        else:
            error("get points error" + r.text)
        return self.points
        

if __name__ == '__main__':
    # client = HDFSFileSystem("192.168.2.21", "root", "wim123")
    # client.refresh()
    # client2 = HDFSFileSystem("192.168.2.21", "root", "wim123")

    # tdir = HDFSDir("/nfs")
    # print(tdir.get_childs())
    p = PointsData()
    p.get_points("/nfs/data/p0/20190715/0-20190715235942622-60000x527.bin",
                 [20, 30, 50])
    # import json
    # print(json.dumps(tdir.get_dict()))