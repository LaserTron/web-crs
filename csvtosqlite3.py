"""
The purpose of this module is to write csv files
from sqlite3 tables and vice-versa.
"""

import csv,web
import cStringIO as csi

def getDbObject(dbfile):
    """
    Returns a web.database object if given a sqlite3 database filename
    otherwise, if already given a web.database object, returns the 
    object.
    """
    if not type(dbfile) is str:
        return dbfile    
    db = web.database(dbn="sqlite", db=dbfile)
    db.ctx.db.text_factory=str
    db.query("PRAGMA journal_mode=off") #living dangerously
    db.query("PRAGMA synchronous=off")
    return db

def getSchema(db,table):
    """
    Returns a pragma query that contains dictionaries describing 
    each column of a table.
    """
    querystring = "pragma table_info('{0}')".format(table)
    return db.query(querystring)
    
    
def sqlite3toCSVstring(db,table):
    """
    Takes a table in a sqlite3 database
    and writes it out as a nice csv string.
    """
    db = getDbObject(db)
    #we need to get table info
    tinfo = getSchema(db,table)
    columns={}
    fields=[]
    for i in tinfo: #make the fieldnames
        columns[i['cid']]=i['name']#great: dicts autosort
    for i in columns:#construct fieldnames
        fields.append(columns[i])

    selection = db.select(table) #returns an iterator of dictionaries
    output = csi.StringIO() #output io
    writer = csv.DictWriter(output,fieldnames=fields)
    writer.writeheader()
    for i in selection:
        writer.writerow(i)
        
    return output.getvalue()

def writeSqlite3TableFromCSV(db,table,csvstr):
    """
    Takes a csv string (optained from a file) and overwrites the 
    table with the csv file. This is done by deleting all the rows 
    and then re-entering them.
    """
    db = getDbObject(db)
    # coltype = {}
    # cols = getSchema(db,table)
    # for i in cols:
    #     coltype['name']=coltype['type']
    inio = csi.StringIO()
    inio.write(csvstr)
    inio.seek(0)
    reader = csv.DictReader(inio)
    db.multiple_insert(table,values=reader,seqname=False)

def emptySqlite3Table(db,table):
    """
    bascally a wrapper for an sql query
    """
    db = getDbObject(db)
    querystr= "DELETE FROM {0}".format(table)
    db.query(querystr)

def csvOverwrite(db,table,csvstring):
    emptySqlite3Table(db,table)
    writeSqlite3TableFromCSV(db,table,csvstring)
    
def getTables(db):
    db = getDbObject(db)
    a = db.select('sqlite_master',what="name")
    return map(lambda x: x['name'],a)

def sqlite3TableToIter(db,table):
    """
    Takes an sqlite3 table and produces an iterator containing the 
    rows of the table, for easy printing.
    """
    #this method is a bit hacky.
    db = getDbObject(db)
    csvstring = sqlite3toCSVstring(db,table)
    inio = csi.StringIO()
    inio.write(csvstring)
    inio.seek(0)
    reader = csv.reader(inio)
    return reader
