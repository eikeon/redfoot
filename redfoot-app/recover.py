from __future__ import generators

from sys import version_info
if version_info[0:2] > (2, 2):
    # Part of Python's standard library
    try:
        from bsddb import db
    except:
        from bsddb3 import db        
else:
    # http://pybsddb.sourceforge.net/
    from bsddb3 import db

from os import mkdir
from os.path import exists
from struct import pack, unpack

from urllib import quote, unquote

from rdflib.Literal import Literal
from rdflib.URIRef import URIRef
from rdflib.BNode import BNode
from rdflib.exceptions import ContextTypeError

class Recover(object):
    def __init__(self):
        super(Recover, self).__init__()
        self.__open = 0
        
    def open(self, path, recover=True):
        homeDir = path        
        envsetflags  = db.DB_CDB_ALLDB
        envflags = db.DB_INIT_MPOOL | db.DB_INIT_CDB | db.DB_THREAD
	if recover:
	    envflags = db.DB_RECOVER | db.DB_CREATE | db.DB_INIT_TXN | db.DB_INIT_MPOOL | db.DB_THREAD #| db.DB_INIT_CDB 
        try:
            if not exists(homeDir):
                mkdir(homeDir)
        except Exception, e:
            print e
        self.env = env = db.DBEnv()
        env.set_cachesize(0, 1024*1024*50)
        #env.set_lg_max(1024*1024)
        env.set_flags(envsetflags, 1)
        env.open(homeDir, envflags | db.DB_CREATE)

        self.__open = 1
        
        dbname = None
        dbtype = db.DB_BTREE
        dbopenflags = db.DB_THREAD
        
        dbmode = 0660
        dbsetflags   = 0

        # create and open the DBs
        self.__contexts = db.DB(env)
        self.__contexts.set_flags(dbsetflags)
        self.__contexts.open("contexts", dbname, dbtype, dbopenflags|db.DB_CREATE, dbmode)
        self.__spo = db.DB(env)
        self.__spo.set_flags(dbsetflags)
        self.__spo.open("spo", dbname, dbtype, dbopenflags|db.DB_CREATE, dbmode)

        self.__pos = db.DB(env)
        self.__pos.set_flags(dbsetflags)
        self.__pos.open("pos", dbname, dbtype, dbopenflags|db.DB_CREATE, dbmode)

        self.__osp = db.DB(env)
        self.__osp.set_flags(dbsetflags)
        self.__osp.open("osp", dbname, dbtype, dbopenflags|db.DB_CREATE, dbmode)

        self.__cspo = db.DB(env)
        self.__cspo.set_flags(dbsetflags)
        self.__cspo.open("cspo", dbname, dbtype, dbopenflags|db.DB_CREATE, dbmode)

        self.__cpos = db.DB(env)
        self.__cpos.set_flags(dbsetflags)
        self.__cpos.open("cpos", dbname, dbtype, dbopenflags|db.DB_CREATE, dbmode)

        self.__cosp = db.DB(env)
        self.__cosp.set_flags(dbsetflags)
        self.__cosp.open("cosp", dbname, dbtype, dbopenflags|db.DB_CREATE, dbmode)

        self.__i2k = db.DB(env)
        self.__i2k.set_flags(dbsetflags)
        
        self.__i2k.open("i2k", dbname, dbtype, dbopenflags|db.DB_CREATE, dbmode)

        self.__k2i = db.DB(env)
        self.__k2i.set_flags(dbsetflags)#|db.DB_RECNUM)
        self.__k2i.open("k2i", dbname, dbtype, dbopenflags|db.DB_CREATE, dbmode)

        self.__namespace = db.DB(env)
        self.__namespace.set_flags(dbsetflags)
        self.__namespace.open("namespace", dbname, dbtype, dbopenflags|db.DB_CREATE, dbmode)

        self.__prefix = db.DB(env)
        self.__prefix.set_flags(dbsetflags)
        self.__prefix.open("prefix", dbname, dbtype, dbopenflags|db.DB_CREATE, dbmode)

        
        next = self.__k2i.get("next")
        if next==None:
            self.__k2i.put("next", "%d" % 1)            
        
    def close(self):
        self.__open = 0
        self.__contexts.close()
        self.__spo.close()
        self.__pos.close()
        self.__osp.close()
        self.__cspo.close()
        self.__cpos.close()
        self.__cosp.close()
        self.__k2i.close()
        self.__i2k.close()
        self.__namespace.close()
        self.__prefix.close()
        self.env.close()

if __name__=="__main__":
    recover = Recover()
    recover.open("__rfdb__")
    recover.close()
