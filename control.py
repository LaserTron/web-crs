import web
import gradebook
import hashlib
import time

#
#Requires a DB with a table called 'States' with columns 'state' and 'page'
#Requires a DB with a tabe called 'Users' with columns 'username' and 'section'

def sha1digest(s):
    ho = hashlib.sha1(s+salt)
    return ho.hexdigest()

ctrl = web.database(dbn="sqlite",db="control.db")
ctrl.ctx.db.text_factory=str #erm... I have NO CLUE what this means :-/

def isInTable(table,col,entry):
    wherestring = '{0}=\"{1}\"'.format(col,entry)
    res = ctrl.select(table,where=wherestring)
    return bool(res)

def getEntry(table,col,key,ID):
    """
    returns value of column from corresponding key/ID. Returns
    only one entry.
    """
    wherestring = "{0}=\"{1}\"".format(key,ID)
    bob = ctrl.select(table,where=wherestring,what=col)
    if bool(bob): #Calling bool(bob) depletes the iterator  
        bob = ctrl.select(table,where=wherestring,what=col)
        return bob[0][col]
    else:
        return None

def isStudent(user):
    return isInTable("students","username",user)

def isInstructor(user):
    return isInTable("instructors","username",user)

def getPassHash(user):
    """
    Returns the hash of the user's password which is stored in control.db or returns false if 
    the user doesn't exist.
    """
    emp = lambda x: x==None or x=="" or x.isspace()
    if isStudent(user):
        paswd = getEntry("students","password","username",user)
        if emp(paswd):
            return None
        else:
            return paswd
    elif isInstructor(user):
        paswd = getEntry("instructors","password","username",user)
        if emp(paswd):
            return None
        else:
            return paswd
    else:
        return False    

def populatePassHash():
    """This method will go through the usernames of all
    students and instructors will assign to the password column the
    sha1digest+salt (see the sha1digest function) of the
    username. This is used for direct login.

    """
    #wherestring="section=\"{0}\"".format(section)
    stus = ctrl.select("students",what='username')
    instrs = ctrl.select("instructors",what='username')
    for i in stus:
        uname = i['username']
        setPassword(uname,uname)#this will salt and hash the username and put it in password
    for i in instrs:
        uname = i['username']
        setPassword(uname,uname)#this will salt and hash the username and put it in password
    #return None

def setPassword(user,paswd):
    """
    Stores a hash of the user's password. Returns false if 
    the user is not found.
    """
    passhash = sha1digest(paswd)
    sqldic={}
    sqldic['where']="username = \"{0}\"".format(user)
    sqldic['password']=passhash
    if isStudent(user):
        ctrl.update("students",**sqldic) 
    elif isInstructor(user):
        ctrl.update("instructors",**sqldic) 
    else:
        return False

def clearPassword(user):
    """
    Deletes the password
    """
    sqldic={}
    sqldic['where']="username = \"{0}\"".format(user)
    sqldic['password']=None
    if isStudent(user):
        ctrl.update("students",**sqldic) 
    elif isInstructor(user):
        ctrl.update("instructors",**sqldic) 
    else:
        return False
    
def validatePassword(user,pashash):
    return pashash == getPassHash(user)

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
    if not nam == None:
        nam = nam.strip()
    else:
        nam = ""
    res = isInTable('sections','name', nam)
    if not res:#no user there
        ctrl.insert('sections', name = nam)

def addStudent(user,sec):#adds a student
    user=user.strip()
    res = isInTable('students','username', user)
    if not res:#no user there
        ctrl.insert('students',username = user, section = sec)
    sec = sec.strip()#ensures section is added as well, if necessary
    res = isInTable('sections','name',sec)
    if not res:
        addSection(sec)

def populateSections():
    """
    This method populates the section list from the student roster.
    """
    #ISSUE this is a hack
    stus = ctrl.select("students")
    for i in stus:
        addStudent(i["username"],i["section"])
    
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

    ctrl.insert("sessions",name = sesname, page=0, state="init")
    
def getInstrSession(instr):
    return getEntry("instructors","session","username",instr)

def setInstrSession(instr,session):
    wherestring = "username = \"{0}\"".format(instr)
    sqldic={'where':wherestring,'session':session}
    ctrl.update("instructors",**sqldic)

def getSessionSection(instr):
    sess = getInstrSession(instr)
    return getEntry("sections","name","session",sess)

def getSessionStudents(instr):
    sec = getSessionSection(instr)
    return getStudentsBySec(sec)

def getSessionPage(session):
    return getEntry("sessions","page","name",session)

def getSessionState(session):
    return getEntry("sessions","state","name",session)

def setSessionState(session,state):
    sqldic={
        "where" : "name = \"{0}\"".format(session),
        "state": state
    }        
    ctrl.update("sessions",**sqldic)

def getStudentSession(user):
    sec = getEntry("students","section","username",user)
    return getEntry("sections","session","name",sec)

def getStudentState(student):
    sess = getStudentSession(student)
    return getEntry("sessions","state","name",sess)

def getStudentPage(user):
    return getSessionPage(getStudentSession(user))

def getUserSession(user):
    if isStudent(user):
        return getStudentSession(user)
    if isInstructor(user):
        return getInstrSession(user)

def getUserPage(user):
    sess = getUserSession(user)
    return getSessionPage(sess)

def getUserState(user):
    sess = getUserSession(user)
    return getSessionState(sess)

def updateEntry(table,col,key,ID,newvalue):
    """
    Enters newvalue in the column corresponding to the given key/ID pair
    """
    wherestring = "{0} = \"{1}\"".format(key,ID)
    sqldict={"where":wherestring, col:newvalue}
    ctrl.update(table,**sqldict) #**converts dict to keywords

def getQuizLength(session):
    """
    Returns the number of questions in the quiz assigned to
    session
    """
    quizstr = gradebook.getSessionQuestions(session)
    quizli = quizstr.split(',')
    return len(quizli)
    
def advanceSession(session):
    """
    Increments the question number. Sets the session to finished if 
    finished.
    """
    length = getQuizLength(session)
    curpage = getSessionPage(session)
    if curpage >= length-1:
        wherestring = "name = \"{0}\"".format(session)
        sqldict={"where":wherestring,"state":"finished","page":curpage+1}
        ctrl.update("sessions",**sqldict)
        return False
    else:
        sqldict={
            "where" : "name = \"{0}\"".format(session),
            "page" : curpage+1,
            "state" : "init"
        }
        ctrl.update("sessions",**sqldict)
        return True

def setUltimatum(instr,duration):
    """
    An ultimatum for timers.
    """
    sess = getInstrSession(instr)
    now = time.time()
    then = now+duration+1
    sqldic={
        "where":"name = \"{0}\"".format(sess),
        "ultimatum":then,
        "state":"ultimatum",
    }
    ctrl.update("sessions",**sqldic)

def giveTimeLeft(user):
    """
    Computes the time left in the ultimatum. If negative,
    sets session to closed. Otherwise returns the string representation of 
    the number of seconds remaining.
    """
    if isInstructor(user):
        sess = getInstrSession(user)
    else:
        sess = getStudentSession(user)
    timeup = getEntry("sessions","ultimatum","name",sess)
    now = time.time()
    left = int(timeup-now)
    if left < -1:
        setSessionState(sess,"closed")
        return "closed"
    return str(left)

