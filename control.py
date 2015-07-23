import web
import gradebook
from hashlib import sha1

#
#Requires a DB with a table called 'States' with columns 'state' and 'page'
#Requires a DB with a tabe called 'Users' with columns 'username' and 'section'

def sha1digest(s):
    salt = "boy this is salty frdew34567uhygfrer6uhgfrtyuhijhbgftrdfg"
    ho = sha1(s+salt)
    return ho.hexdigest()

ctrl = web.database(dbn="sqlite",db="control.db")
ctrl.ctx.db.text_factory=str #erm... I have NO CLUE what this means :-/


def isInTable(table,col,entry):
    wherestring = '{0}=\"{1}\"'.format(col,entry)
    res = ctrl.select(table,where=wherestring)
    return bool(res)

def getEntry(table,col,key,ID):
    """
    returns value of column from corresponding key/ID
    """
    wherestring = "{0}=\"{1}\"".format(key,ID)
    bob = ctrl.select(table,where=wherestring,what=col)
    return bob[0][col]

# def getState(section):
#     return getEntry(sessions,state,'section',section)

def setState(page,st):#UPDATE
    wherestring = "page=\"{0}\"".format(page)
    ctrl.update("States", where=wherestring, state=st)
    
def addInstructor(user):
    user=user.strip()
    res = isInTable('instructors','username',user)
    if not res:
        ctrl.insert('instructors', username=user)
        
# def getUserSection(user):
#     wherestring="username=\"{0}\"".format(user)
#     bob=ctrl.select('Users', where=wherestring, what='section')
#     return bob[0]['section']

def delUser(user):#UPDATE
    wherestring="username=\"{0}\"".format(user)
    ctrl.delete('Users',where=wherestring)

def assignInstructor(instr,section):
    wherestring = 'name=\'{0}\''.format(section)
    ctrl.update("sections", where=wherestring, instructor=instr)

def assignSession(qu,section):
    wherestring = 'name=\'{0}\''.format(section)
    ctrl.update("sections", where=wherestring, session=qu)    

def getSections():
    """
    Returns list of section names
    """
    bob= ctrl.select('sections',what='name')
    output = []
    for i in bob:
        output.append(i['name'])
    return output

def getAssignedQuiz(sec):
    """
    Returns the quiz currently assigned to a section
    """
    return getEntry('sections','session','name',sec)
    
def getInstrSections(instr):
    """
    Returns list of sections assigned to an instructor
    """
    wherestring = 'instructor = \"{0}\"'.format(instr)
    bob= ctrl.select('sections',what='name',where=wherestring)
    output = []
    for i in bob:
        output.append(i['name'])
    return output
    

def addSection(nam):
    nam=nam.strip()
    res = isInTable('sections','name', nam)
    if not res:#no user there
        ctrl.insert('sections', name = nam)

def addStudent(user,sec):#adds a user whose role is either
    user=user.strip()
    res = isInTable('students','username', user)
    if not res:#no user there
        ctrl.insert('students',username = user, section = sec)
    sec = sec.strip()#ensures section is added as well, if necessary
    res = inInTable('sections','name',sec)
    if not res:
        addSection(sec)

def getStudentsBySec(section):
    """
    Returns the list of student usernames in a given section
    """
    wherestring = "section = \"{0}\"".format(section)
    students = ctrl.select("students",where=wherestring)
    output = []
    for i in students:
        output.append(i['username'])
    return output

def sessionAdd(sesname):
    """
    Adds an entry to the sessions table with initialized states
    """
    if isInTable("sessions","name",sesname):
        return None

    ctrl.insert("sessions",name = sesname, page=0, state="closed")
    
def getInstrSession(instr):
    return getEntry("instructors","session","username",instr)

def setInstrSession(instr,session):
    wherestring = "username = \"{0}\"".format(instr)
    sqldic={'where':wherestring,'session':session}
    ctrl.update("instructors",**sqldic)

def getSessionPage(session):
    return getEntry("sessions","page","name",session)

def getSessionState(session):
    return getEntry("sessions","state","name",session)

def getStudentSession(user):
    sec = getEntry("students","section","username",user)
    return getEntry("sections","session","name",sec)

def getStudentState(student):
    sess = getStudentSession(student)
    return getEntry("sessions","state","name",sess)

def getStudentPage(user):
    return getSessionPage(getStudentSession(user))

def updateEntry(table,col,key,ID,newvalue):
    """
    Enters newvalue in the column corresponding to the given key/ID pair
    """
    wherestring = "{0} = \"{1}\"".format(key,ID)
    sqldict={"where":wherestring, col:newvalue}
    ctrl.update(table,**sqldict) #**converts dict to keywords

def advanceSession(session):
    """
    Increments the question number. Sets the session to finished if 
    finished.
    """
    quizstr = gradebook.getSessionQuestions(session)
    quizli = quizstr.split(',')
    length = len(quizli)
    curpage = getSessionPage(session)
    if curpage >= length-1:
        wherestring = "name = \"{0}\"".format(session)
        sqldict={"where":wherestring,"state":"finished","page":curpage+1}
        ctrl.update("sessions",**sqldict)
        return False
    else:
        updateEntry("sessions","page","name",session,curpage+1)
        return True
