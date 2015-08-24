import web
import sqlite3
import gradebook 
import clickerQuestions as cq
import time

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
    """
    Inserts a question with the given ID and returns 1 if there 
    is no question with that id. If there is already a question with 
    that id return 0.
    """
    if isInTable('questionbank', 'id', ID):
        return 0
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
        return 1

def updateQuestion(ID,tgs,qblck):
    """
    Rewrites the question with a given tag and qblock.
    """
    if isInTable('questionbank','id',ID):
        sqldic = {
            "ID":ID+"-"+str(time.time()),
            "qblock":qblck
        }
        qu.insert("old",**sqldic)
        sqldic={
            "where":"ID=\"{0}\"".format(ID),
            "tags":tgs,
            "qblock":qblck
        }
        qu.update("questionbank",**sqldic)
    else:
        addQuestion(ID,tgs,qblck)
        
def delQuestion(ID):
    wherestring="id=\"{0}\"".format(ID)
    qu.delete('questionbank',where=wherestring)

def clearQuestions():
    """
    Clears the question bank in the database.
    """
    sqlstring ="DROP TABLE questionbank"
    qu.query(sqlstring)
    sqlstring = "CREATE TABLE questionbank(id TEXT, tags TEXT, qblock TEXT)"
    qu.query(sqlstring)

def mkQuestions():
    """
    Creates a new blank questionbank table in questions.db
    """
    sqlstring = "CREATE TABLE questionbank(id TEXT, tags TEXT, qblock TEXT)"
    qu.query(sqlstring)

def addQuiz(ID):
    """
    Adds an empty quiz if none exists in DB
    """
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

#THESE METHODS TO IMPORT/EXPORT CLICKER BANK

# def openFile(filename):
#     f = open(filename,'r')
#     return f
#
# def dumpFileToString(filename):
#     f=openFile(filename)
#     content = f.read()
#     f.close()
#     return content 
#
# def loadBank():
#     output = []
#     qbank = dumpFileToString(banklocation)
#     qus = cq.extractQuestions(qbank)
#     for qblock in qus:
#         output.append(cq.clkrQuestion(qblock))
#     return output

# def populateBank():
#     qus = loadBank()
#     for i in qus:
#         i.addToDb()
        
# def rePopulateBank():
#     clearQuestions()
#     populateBank()

def updateBank(uplstr):
    """
    Takes a string representing a LaTex question bank, and adds 
    quizzes whose IDs are not in the questionbank.    
    """
    qus = cq.extractQuestions(uplstr)
    clkrs = map(cq.clkrQuestion,qus)
    for i in clkrs: i.addToDb()    
    
def questionsToTexStr():
    "Produces a string that can be written to a tex file"
    qus = qu.select("questionbank")
    qblocks = []
    for i in qus: qblocks.append(i["qblock"])
    pre = """\\documentclass{article}
\\usepackage{geometry,amssymb,graphicx,enumerate}
    
\\newenvironment{clkrQuestion}[2]{
\\begin{minipage}{\\textwidth}
\\vskip .4in
\\textbf{Id:}\\texttt{#1}\\\\ 
\\textbf{Tags:}{~#2}\\\\
}
{\\end{minipage}}

\\newcommand{\\answer}[1]{\\textbf{Answer: }\\ref{#1}}
\\newcommand{\\explanation}[1]{#1}
\\newcommand{\\probstmt}[1]{#1}
\\begin{document}
"""

    middle = "\n".join(qblocks)

    post="\n \\end{document}"

    return pre+middle+post
