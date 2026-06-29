-- RADIUS veritabanı şeması

CREATE TABLE IF NOT EXISTS radcheck (
    id SERIAL PRIMARY KEY,
    username VARCHAR(64) NOT NULL DEFAULT '',
    attribute VARCHAR(64) NOT NULL DEFAULT '',
    op VARCHAR(2) NOT NULL DEFAULT '==',
    value VARCHAR(253) NOT NULL DEFAULT ''
);
CREATE INDEX radcheck_username ON radcheck(username, attribute);

CREATE TABLE IF NOT EXISTS radreply (
    id SERIAL PRIMARY KEY,
    username VARCHAR(64) NOT NULL DEFAULT '',
    attribute VARCHAR(64) NOT NULL DEFAULT '',
    op VARCHAR(2) NOT NULL DEFAULT '=',
    value VARCHAR(253) NOT NULL DEFAULT ''
);
CREATE INDEX radreply_username ON radreply(username, attribute);

CREATE TABLE IF NOT EXISTS radusergroup (
    id SERIAL PRIMARY KEY,
    username VARCHAR(64) NOT NULL DEFAULT '',
    groupname VARCHAR(64) NOT NULL DEFAULT '',
    priority INTEGER NOT NULL DEFAULT 1
);
CREATE INDEX radusergroup_username ON radusergroup(username);

CREATE TABLE IF NOT EXISTS radgroupreply (
    id SERIAL PRIMARY KEY,
    groupname VARCHAR(64) NOT NULL DEFAULT '',
    attribute VARCHAR(64) NOT NULL DEFAULT '',
    op VARCHAR(2) NOT NULL DEFAULT '=',
    value VARCHAR(253) NOT NULL DEFAULT ''
);
CREATE INDEX radgroupreply_groupname ON radgroupreply(groupname, attribute);

CREATE TABLE IF NOT EXISTS radacct (
    radacctid SERIAL PRIMARY KEY,
    acctsessionid VARCHAR(64) NOT NULL DEFAULT '',
    acctuniqueid VARCHAR(32) NOT NULL DEFAULT '',
    username VARCHAR(64) NOT NULL DEFAULT '',
    realm VARCHAR(64) DEFAULT '',
    nasipaddress INET,
    nasportid VARCHAR(32) DEFAULT NULL,
    nasporttype VARCHAR(32) DEFAULT NULL,
    acctstarttime TIMESTAMP WITH TIME ZONE,
    acctupdatetime TIMESTAMP WITH TIME ZONE,
    acctstoptime TIMESTAMP WITH TIME ZONE,
    acctinterval INTEGER,
    acctsessiontime INTEGER,
    acctauthentic VARCHAR(32) DEFAULT NULL,
    connectinfo_start VARCHAR(50) DEFAULT NULL,
    connectinfo_stop VARCHAR(50) DEFAULT NULL,
    acctinputoctets BIGINT,
    acctoutputoctets BIGINT,
    calledstationid VARCHAR(50) NOT NULL DEFAULT '',
    callingstationid VARCHAR(50) NOT NULL DEFAULT '',
    acctterminatecause VARCHAR(32) NOT NULL DEFAULT '',
    servicetype VARCHAR(32) DEFAULT NULL,
    framedprotocol VARCHAR(32) DEFAULT NULL,
    framedipaddress INET
);
CREATE INDEX radacct_username ON radacct(username);
CREATE INDEX radacct_sessionid ON radacct(acctsessionid);

-- Varsayılan test verileri
-- PAP Doğrulaması için şifre (Cleartext-Password veya bcrypt kullanılabilir. Basitlik için Cleartext)
INSERT INTO radcheck (username, attribute, op, value) VALUES ('s3m_admin', 'Cleartext-Password', ':=', 'testing123');

-- MAB için MAC Adresi doğrulaması (Auth-Type := Accept)
INSERT INTO radcheck (username, attribute, op, value) VALUES ('AA:BB:CC:DD:EE:FF', 'Auth-Type', ':=', 'Accept');

-- Gruplar
INSERT INTO radusergroup (username, groupname, priority) VALUES ('s3m_admin', 'admin', 1);
INSERT INTO radusergroup (username, groupname, priority) VALUES ('AA:BB:CC:DD:EE:FF', 'devices', 1);

-- Grup bazlı VLAN atamaları (admin vlan 10, devices vlan 20)
INSERT INTO radgroupreply (groupname, attribute, op, value) VALUES ('admin', 'Tunnel-Type', '=', '13');
INSERT INTO radgroupreply (groupname, attribute, op, value) VALUES ('admin', 'Tunnel-Medium-Type', '=', '6');
INSERT INTO radgroupreply (groupname, attribute, op, value) VALUES ('admin', 'Tunnel-Private-Group-Id', '=', '10');

INSERT INTO radgroupreply (groupname, attribute, op, value) VALUES ('devices', 'Tunnel-Type', '=', '13');
INSERT INTO radgroupreply (groupname, attribute, op, value) VALUES ('devices', 'Tunnel-Medium-Type', '=', '6');
INSERT INTO radgroupreply (groupname, attribute, op, value) VALUES ('devices', 'Tunnel-Private-Group-Id', '=', '20');