import web
import sqlite3 #unfortunately web.db has some inconveniences
import sys

import control


#
# Requires a database with tables for sections, each table hasa a 'username' column
#

gdbk = web.database(dbn="sqlite",db="gradebook.db")

def isInTable(table,col,entry):
    wherestring = '{0}=\"{1}\"'.format(col,entry)
    res = gdbk.select(table,where=wherestring)
    return bool(res)

def addColumn(table,col):#you don't want to use this one too often, this is a bit of a hack, actually
    con = sqlite3.connect('gradebook.db')
    cur = con.cursor()
    sqlstring ="ALTER TABLE {0} ADD COLUMN {1} TEXT".format(table,col)
    cur.execute(sqlstring)
    con.commit()
    con.close()

def addStudent(student,section):
    student=student.strip()
    res = isInTable(section, 'username', student)
    if not bool(res):
        gdbk.insert(section, username = student)
    
def setAnswer(student,choice,value):#This is a bit of a hack...
    con = sqlite3.connect('gradebook.db')
    cur = con.cursor()
    value=str(value)#in case saved as int
    section = control.getUserSection(student)
    sqlstring = "UPDATE {0} SET {1}=\'{2}\' WHERE username=\'{3}\'".format(section,choice,value,student)
    # print section
    #print sqlstring
    cur.execute(sqlstring)
    con.commit()
    con.close()
    
