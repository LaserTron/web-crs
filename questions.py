import web
import sqlite3
import gradebook 
import clickerQuestions as cq

print "questions"
qu = web.database(dbn="sqlite",db="questions.db")
qu.ctx.db.text_factory=str #erm... I have NO CLUE what this means :-/
qu.query("PRAGMA journal_mode=off")
qu.query("PRAGMA synchronous=off")

banklocation = 'questions/questionbank.tex'

def cleanCSL(csl):
    """
    Takes a string representing a comma separated list and removes spaces and trailing colons
    """
    csl = csl.replace(' ','')
    return csl.strip(',')

def isInTable(table,col,entry):
    """
    Returns bolean 
    """
    wherestring = '{0}=\"{1}\"'.format(col,entry)
    res = qu.select(table,where=wherestring)
    return bool(res)

def getEntry(table,col,key,ID):
    """
    returns value of column from corresponding key/ID
    """
    wherestring = "{0}=\"{1}\"".format(key,ID)
    bob = qu.select(table,where=wherestring,what=col)
    return bob[0][col]

def getWithTag(tag):
    wherestring = 'tags LIKE \'%{0}%\''.format(tag)
    res = qu.select('questionbank',where=wherestring)
    output = []
    for i in res:
        output.append(i['qblock'])
    return output

def getQuestion(ID):
    """
    Returns a string that is a latex clkrQuestion snippet, i.e.
    a qblock
    """
    wherestring = 'id=\"{0}\"'.format(ID)
    res = qu.select('questionbank',where=wherestring)
    if bool(res):
        return list(res)[0]['qblock']
    else:
        return None
    
def addQuestion(ID,tgs,qblck):
    if isInTable('questionbank', 'id', ID):
        return False
    else:
        #########
        #Need to invoke this block on demand
        #########
        qu.ctx.db.text_factory=str #erm... I have NO CLUE what this means :-/
        qu.query("PRAGMA journal_mode=off")
        qu.query("PRAGMA synchronous=off")
        #############
        #END
        #############
        qu.insert('questionbank', id=ID, tags=tgs, qblock=qblck)
        return True

def delQuestion(ID):
    wherestring="id=\"{0}\"".format(ID)
    qu.delete('questionbank',where=wherestring)

def clearQuestions():
    """
    Clears the question bank in the database.
    """
    #Issue: this can probably be done in a couple lines
    con = sqlite3.connect('questions.db')
    cur = con.cursor()
    sqlstring ="DROP TABLE questionbank"
    cur.execute(sqlstring)
    sqlstring = "CREATE TABLE questionbank(id TEXT, tags TEXT, qblock TEXT)"
    cur.execute(sqlstring)
    con.commit()
    con.close()

def mkQuestions():
    """
    Creates a new blank questionbank table in questions.db
    """
    con = sqlite3.connect('questions.db')
    cur = con.cursor()
    sqlstring = "CREATE TABLE questionbank(id TEXT, tags TEXT, qblock TEXT)"
    cur.execute(sqlstring)
    con.commit()
    con.close()

def addQuiz(ID):
    if isInTable('quizzes','id',ID):
        return False
    else:
        qu.insert('quizzes',id = ID, questions='')

def getQuizQuestions(ID):
    """
    Returns comma separated string of question ids
    """
    if isInTable('quizzes','id',ID):
        return getEntry('quizzes','questions','id',ID)
    else:
        return None

def getQblocks(ID):
    """
    Returns the list of qblocks corresponding to a quiz
    """
    qstr = getQuizQuestions(ID)
    qlist = qstr.split(',')
    qblocklist = map(getQuestion,qlist)
    return qblocklist
    
def setQuizQuestions(ID,qstr):
    """
    takes a string that is a comma separated list and 
    writes it in the \"questions\" column.
    """
    qstr=cleanCSL(qstr)
    if isInTable('quizzes','id',ID):
        wherestring = "id=\"{0}\"".format(ID)
        qu.update('quizzes',wherestring, questions=qstr)

def getQuizzes():
    """
    Returns list of quiz ids
    """
    bob= qu.select('quizzes',what='id')
    output = []
    for i in bob:
        output.append(i['id'])
    return output

def giveClickerQuestion(session,page):
    """
    Returns the clickerquestion corresponding to a page on 
    a session
    """
    qstr = gradebook.getSessionQuestions(session)
    print qstr
    qlist = qstr.split(',')
    qid=qlist[page]
    qblock = getQuestion(qid)
    return cq.clkrQuestion(qblock)

#THESE METHODS TO IMPORT CLICKER BANK

def openFile(filename):
    f = open(filename,'r')
    return f

def dumpFileToString(filename):
    f=openFile(filename)
    content = f.read()
    f.close()
    return content

def loadBank():
    output = []
    qbank = dumpFileToString(banklocation)
    #qbank = unicode(qbank)
    qus = cq.extractQuestions(qbank)
    for qblock in qus:
        output.append(cq.clkrQuestion(qblock))
    return output

def populateBank():
    qus = loadBank()
    for i in qus:
        i.addToDb()

def rePopulateBank():
    clearQuestions()
    populateBank()

