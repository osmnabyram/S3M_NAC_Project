from sqlalchemy import Column, Integer, String, DateTime, BigInteger
from datetime import datetime
from database import Base

class RadCheck(Base):
    __tablename__ = "radcheck"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    attribute = Column(String)
    op = Column(String, default="==")
    value = Column(String)

class RadReply(Base):
    __tablename__ = "radreply"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    attribute = Column(String)
    op = Column(String, default="=")
    value = Column(String)

class RadUserGroup(Base):
    __tablename__ = "radusergroup"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    groupname = Column(String)
    priority = Column(Integer, default=1)

class RadGroupReply(Base):
    __tablename__ = "radgroupreply"
    id = Column(Integer, primary_key=True, index=True)
    groupname = Column(String, index=True)
    attribute = Column(String)
    op = Column(String, default="=")
    value = Column(String)

class RadAcct(Base):
    __tablename__ = "radacct"
    radacctid = Column(Integer, primary_key=True, index=True)
    acctsessionid = Column(String, index=True)
    acctuniqueid = Column(String)
    username = Column(String, index=True)
    realm = Column(String)
    nasipaddress = Column(String)
    nasportid = Column(String)
    nasporttype = Column(String)
    acctstarttime = Column(DateTime)
    acctupdatetime = Column(DateTime)
    acctstoptime = Column(DateTime)
    acctinterval = Column(Integer)
    acctsessiontime = Column(Integer)
    acctauthentic = Column(String)
    connectinfo_start = Column(String)
    connectinfo_stop = Column(String)
    acctinputoctets = Column(BigInteger)
    acctoutputoctets = Column(BigInteger)
    calledstationid = Column(String)
    callingstationid = Column(String)
    acctterminatecause = Column(String)
    servicetype = Column(String)
    framedprotocol = Column(String)
    framedipaddress = Column(String)