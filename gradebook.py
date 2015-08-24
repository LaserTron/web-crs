import web
import sqlite3 #unfortunately web.db has some inconveniences
import sys


import control
import questions
import clickerQuestions as cq

#
# Requires a database with tables for sections, each table hasa a 'username' column
#

# ISSUES:
# sqlite3 module is no longer necessary since we can use 
# gdbk.query(foo) instead of cur.execute(foo). Also using keyword
# dictionnaries, we can pass keys as arguments.

gdbk = web.database(dbn="sqlite",db="gradebook.db")
gdbk.ctx.db.text_factory=str #erm... I have NO CLUE what this means :-/

#These speed stuff up thanks http://stackoverflow.com/questions/21590824/sqlite-updating-one-record-is-very-relatively-slow
gdbk.query("PRAGMA journal_mode=off")
gdbk.query("PRAGMA synchronous=off")

def remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text #or whatever

def getEntry(table,col,key,ID):
    """
    Returns value of column from corresponding key/ID.
    """
    wrcol = "\""+col+"\""
    wherestring = "{0}=\"{1}\"".format(key,ID)
    bob = gdbk.select(table,where=wherestring,what=wrcol)
    return bob[0][col]

def updateEntry(table,col,key,ID,newvalue):
    """
    Enters newvalue in the column corresponding to the given key/ID pair
    """
    wherestring = "{0} = \"{1}\"".format(key,ID)
    sqldict={"where":wherestring, col:newvalue}
    gdbk.update(table,**sqldict) #**converts dict to keywords
    
def isInTable(table,col,entry):
    wherestring = '{0}=\"{1}\"'.format(col,entry)
    res = gdbk.select(table,where=wherestring)
    return bool(res)

def addColumn(table,col):#you don't want to use this one too often, this is a bit of a hack, actually
    con = sqlite3.connect('gradebook.db')
    cur = con.cursor()
    sqlstring ="ALTER TABLE {0} ADD COLUMN \"{1}\" TEXT".format(table,col)
    cur.execute(sqlstring)
    con.commit()
    con.close()

def addIntCol(table,col):#you don't want to use this one too often, this is a bit of a hack, actually
    con = sqlite3.connect('gradebook.db')
    cur = con.cursor()
    sqlstring ="ALTER TABLE {0} ADD COLUMN \"{1}\" INTEGER".format(table,col)
    cur.execute(sqlstring)
    con.commit()
    con.close()

def addFloatCol(table,col):#you don't want to use this one too often, this is a bit of a hack, actually
    con = sqlite3.connect('gradebook.db')
    cur = con.cursor()
    sqlstring ="ALTER TABLE {0} ADD COLUMN \"{1}\" FLOAT".format(table,col)
    cur.execute(sqlstring)
    con.commit()
    con.close()
    
def addStudent(student,session):
    """
    Adds a student to a session
    """
    student=student.strip()
    res = isInTable(session, 'username', student)
    if not bool(res):
        gdbk.insert(session, username = student)
    
def setAnswer(student,choice,value):#This is a bit of a hack...
    #con = sqlite3.connect('gradebook.db')
    #cur = con.cursor()
    value=str(value)#in case saved as int
    section = control.getUserSection(student)
    sqlstring = "UPDATE {0} SET {1}=\'{2}\' WHERE username=\'{3}\'".format(section,choice,value,student) #this can be fixed with a keyword dict
    # print section
    #print sqlstring
    #cur.execute(sqlstring)
    #con.commit()
    #con.close()
    gdbk.query(sqlstring)

    
def makeSession(sname,qid):
    """makes a table called sname+RESPONSES.Tables have a username
    column, a column corresponding to a question to record a grade
    and and columns to record responses.
    quiz id: Q+<integer>
    quiz question: Qqq <-- concatenate digit
    quiz choice Qqq "choice" IDC <-- concatenate choice id
    """
    if isInTable("sessions","name",sname):
        return False

    qblocks = questions.getQblocks(qid)
    qlist = map(cq.clkrQuestion,qblocks)        
    sqlstring = "CREATE TABLE {0}(username TEXT)".format(sname)
    gdbk.query(sqlstring)

    qcounter = 0
    for clq in qlist:
        basename = "Q"+str(qcounter)
        totcol = basename+"total"
        addFloatCol(sname, basename)#new check if works
        addFloatCol(sname,totcol)
        cd = clq.getChoiceDict()
        for i in cd:
            colname = basename+i
            addIntCol(sname,colname)
        qcounter+=1

    qstr = questions.getQuizQuestions(qid)    
    gdbk.insert('sessions', name=sname, quiz=qid, questions=qstr)

def getQuizFromSession(session):
    return getEntry('sessions','quiz','name',session)

def getSessionQuestions(session):
    return getEntry('sessions','questions','name',session)

def getStudentSelections(student,session,qnumber):
    """
    Returns a list of answerids of the student's selection
    """
    quizID = getEntry('sessions', 'quiz', 'name', session)
    qblock = questions.getQblocks(quizID)[qnumber]
    clkq = cq.clkrQuestion(qblock)
    basename = "Q"+str(qnumber)
    choices = clkq.getChoices()
    selections = []
    sqldic = {'where':"username = \"{0}\"".format(student)}
    row = gdbk.select(session,**sqldic)[0]
    for c in choices:
        if row[basename+c] == 1:
            selections.append(c)
    return selections
            
def toggleChoice(student,session,qnumber,choice):
    """
    Changes the value of a student choice and updates the 
    grade at the same time. This is the method that works hardest, so
    database calls are minimized. Update is expensive.
    """
    qustr = getSessionQuestions(session)
    quli = qustr.split(",")
    qid= quli[qnumber]
    qblock = questions.getQuestion(qid)
    clkq = cq.clkrQuestion(qblock)
    currentq = "Q"+str(qnumber)
    currentc = currentq+choice
    wherestring = 'username = \"{0}\"'.format(student)
    dbrow = gdbk.select(session,where=wherestring)[0]

    #First we toggle the value in the response area
    curEntry = dbrow[currentc]
    #return curEntry
    if curEntry == 1:
        curEntry = 0
    else:
        curEntry = 1
        
    #After toggling the entry we update the score
    curScore = dbrow[currentq]
    if curScore == None:
        curScore =0
    if clkq.checkAnswer(choice):
        print "Correct"
        grade = 1
    else:
        print "Wrong"
        grade = -1
    if curEntry == 1:
        curScore = curScore + grade
    else:
        curScore = curScore - grade
    
    total = clkq.getTotal()
    grade = max(float(curScore)/total,0)
    wherestring = "username = \"{0}\"".format(student)
    updatedic={'where':wherestring,currentc:curEntry,currentq:curScore,currentq+"total":grade}
    gdbk.update(session,**updatedic)
    return curEntry 

def tallyAnswers(session,qnumber):
    """
    Counts the responses to a question and returns a dictionary
    """
    quizID = getEntry('sessions', 'quiz', 'name', session)
    qblock = questions.getQblocks(quizID)[qnumber]
    clkq = cq.clkrQuestion(qblock)
    basename = "Q"+str(qnumber)
    results = {}
    choices = clkq.getChoices()
    total=0

    #count total number of entries (some students may be absent)
    bob = gdbk.select(session, what=basename)
    for i in bob:
        if not(i[basename] == None):
            total+=1
    results["Total responses"]=total

    #add up individual selections
    for i in choices:
        name=i
        choice = basename+i
        bob = gdbk.select(session, what = choice)
        selected = 0
        for i in bob:
            if i[choice]==1:
                selected +=1
        results[name+"count"]=selected
        if total == 0:
            perc = 0
        else:
            perc = int(float(selected)/float(total)*100)
        results[name] = perc
    return results

    
