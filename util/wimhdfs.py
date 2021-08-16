#!/usr/bin/env python

import sys
# from snakebite.client import Client
from hdfs import InsecureClient
import datetime

http_addr = 'http://192.168.2.80:14000'

class HDFSObject(object):


    def __init__(self, path, parent=None):
        self.path = path
        self.parent = parent
        self.childs = []
        # self.row = -1
        self.modtime = 0
        self.length = 0

    def __len__(self):
        return len(self.childs)

    def get_dict(self):
        pass

class HDFSDir(HDFSObject):

    # path = ""
    # childs = []
    def __init__(self, path, parent=None):
        super(HDFSDir, self).__init__(path, parent)

    def refresh(self):
        self.childs = self.get_childs()
        

    def get_childs(self):
        childs = []
        # TODO set in config file
        client = InsecureClient(http_addr, user='root')
        # client = Client('hmaster', 9000)
        print(self.path)
        for x in client.list(self.path):
            # print(x)
            attr = client.status(self.path + "/" + x, strict=False)
            # print(attr)
            if attr is None:
                continue
            if attr['type'] == "FILE":
                # print(attr)
                ch = HDFSFile(self.path + "/" + x, self)
            elif attr['type'] == "DIRECTORY":
                ch = HDFSDir(self.path+ "/" + x, self)
                ch.refresh()
            ch.length = attr["length"]
            timestamp = attr["modificationTime"]/1000
            # # print(type(timestamp))
            # # if timestamp > 0:
            #     # print(timestamp)
            ch.modtime = datetime.datetime.fromtimestamp(timestamp)
            # # print(type(ch.modtime))
          
            childs.append(ch)
        return childs

    def get_dict(self):
        files = []
        dirs = []
        for x in self.childs:
            if isinstance(x, HDFSDir):
                chdir_dict = x.get_dict()
                dirs.append(chdir_dict)
            if isinstance(x, HDFSFile):
                chfile_dict = x.get_dict()
                files.append(chfile_dict)
        return {"path": self.path, "files": files, "folders": dirs}
    
        

    # def data(self, column):
    #     # print(name)
    #     if column == 0:
    #         return self.path.split("/")[-1]
    #     else:
    #         return self.path

    # def add_child(self, child):
    #     self.childs.append(child)

    # def clear(self):
    #     for ch in self.childs:
    #         if isinstance(ch, HDFSDir):
    #             ch.clear()
    #     del self.childs[:]


class HDFSFile(HDFSObject):
    # path = ""
    def __init__(self, path, parent=None):
        super(HDFSFile, self).__init__(path, parent)

    def data(self, column):
        if column == 0:
            return self.path.split("/")[-1]
        else:
            return self.path

    def get_dict(self):
        return {"path": self.path, "files": [], "folders":[]}

    def download(self, dstPath):
        # TODO set a function to get client
        # client = Client("hmaster", 9000)
        client = InsecureClient(http_addr, user='root')
        # return generator
        name = self.path.split("/")[-1]
        print(name)
        try:
            res = client.download(self.path, dstPath + "/" + name)
        
            # ret = next(res)
            print(res)
            '''
            'result': True, 'error': ''
            if ret["result"] is True:
                return ret["path"]
            else:
                return None
            '''
        except Exception as e:
            print(e)
            return None



if __name__ == '__main__':
    # client = HDFSFileSystem("192.168.2.21", "root", "wim123")
    # client.refresh()
    # client2 = HDFSFileSystem("192.168.2.21", "root", "wim123")

    # tdir = HDFSDir("/nfs")
    # print(tdir.get_childs())
    tdir = HDFSDir("./")
    tdir.refresh()
    # import json
    # print(json.dumps(tdir.get_dict()))
    