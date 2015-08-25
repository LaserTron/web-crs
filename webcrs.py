import web
import control
import gradebook
import time
from time import sleep
from web import form
import questions
import clickerQuestions as cq
import pureClick as pq
import csvtosqlite3 as csvsql

############
# This block is supposed to get HTTPS going.
# reference:  http://webpy.org/cookbook/ssl
# It does not work
#############
# from web.wsgiserver import CherryPyWSGIServer
# CherryPyWSGIServer.ssl_certificate = "ssl/clicker-webapp.cert"
# CherryPyWSGIServer.ssl_private_key = "ssl/clicker-webapp.key"
############
#End HTTPS block.
#############

#############
#Issues:
#############
#
#
#
#############

urls = (#this delcares which url is activated by which class
    '/', 'index',
    '/comet/', 'Comet',
    '/quiz/(.+)','question',
    '/conduct/(.+)','conduct',
    '/submit/(.+)', 'submit',
    '/addQuiz/', 'addQuiz',
    '/assemble/' , 'assemble',
    '/preview/','preview',
    '/instructor/', 'instructor',
    '/logout/', 'logout',
    '/manage/', 'manage',
    '/assign/', 'assign',
    '/sessions/', 'sessions',
    '/databases/','databases',
    '/dbview/(.+)','dbview',
    '/download/(.+)','download',
    '/upload/(.+)','upload',
    '/clearPass/','clearPass',
    '/dropPass/','dropPass',
    '/edit/','edit',
    '/new/','new',
    '/viewQuestion/','viewQuestion',
    '/uploadImg/','uploadImg'
)

render = web.template.render('templates/')
bootpre = render.bootPreamble()
mathpre = render.bootMathJaxPreamble()

questionBankLocation = cq.banklocation
rosters = { #these are pairs of where the database tables
    "students":["control.db","students"],
    "instructors":["control.db","instructors"],
}


def getUsername():
    username=web.cookies().get('clicker-username')
    if username == None:
        raise web.seeother("/?msg=notfound")
    else:
        return username

def getPassHash():
    passhash=web.cookies().get('clicker-passhash')
    if passhash == None:
        raise web.seeother("/?msg=notfound")
    else:
        return passhash

def validateInstructor():
    """
    This method verifies that the user is an instructor 
    by testing the username/password pair. If it's good, return the
    username. Otherwise log the user out.
    """
    username = getUsername()
    passhash=getPassHash()
    if control.isInstructor(username) and control.validatePassword(username,passhash):
        print username + " validated"
        return username
    else:
        raise web.seeother('/logout/?msg=unauthorized')

def validateStudent():
    username = getUsername()
    passhash=getPassHash()
    if control.isStudent(username) and control.validatePassword(username,passhash):
        print username + " validated"
        return username
    else:
        raise web.seeother('/logout/?msg=unauthorized')

def validateUser():
    """
    Returns the username if the user cookies match the database. 
    Otherwise logs out the user.
    """
    username = getUsername()
    passhash=getPassHash()
    if control.validatePassword(username,passhash):
        return username
    else:
        raise web.seeother('/logout/?msg=unauthorized')
    
def cleanCSL(csl):
    """
    Takes a string representing a comma separated list and removes spaces and trailing colons
    """
    csl = csl.replace(' ','')
    return csl.strip(',')
    
class index:
    def GET(self):
        username=web.cookies().get('clicker-username')
        if username == None:
            wi = web.input()
            if "msg" in wi:
                status = wi["msg"]
            else:
                status="clear"
            message = {#This gives a message associated to a status
                "logout":"Cookies deleted. Logged out",
                "notfound":"Username not found. Are you registered? Did you enter the correct username?",
                "unauthorized":"Either wrong password or attempted unauthorized access. You are logged out.",
                "clear":"Enter your new password if first time use or password reset.",
                "newpass":"Your password has been cleared. Please enter your username and new password."
            }
            return render.login(bootpre,message[status])

        if control.isInTable('instructors','username',username):
            destination = '/instructor/'
        elif control.isInTable('students','username',username):
            destination = '/quiz/{0}'.format(username)
        else:
            raise web.seeother("/logout/?msg=notfound")

        raise web.seeother(destination)
            
    def POST(self):
        i = web.input()
        username=i.username
        password=i['password']
        passhash = control.sha1digest(password)
        if control.getPassHash(username) == None:
            control.setPassword(username,password)
        web.setcookie('clicker-username', username)
        web.setcookie('clicker-passhash', passhash)
        raise web.seeother("/")


class question:
    def GET(self,username):
        student = validateStudent()#ensures credentials are okay
        if not student==username:
            raise web.seeother("/logout/?msg=unauthorized")
        sess = control.getStudentSession(username)
        page = control.getSessionPage(sess)
        state = control.getSessionState(sess)
        if state == "finished":
            return render.studentFinished() 
        tally = gradebook.tallyAnswers(sess,page)
        clkq = questions.giveClickerQuestion(sess,page)

        #STATE SWITCH
        if state == "init":
            content = render.notReady()
        elif state == "open" or state =="ultimatum":
            content = clkq.getRendered()
        elif state == "closed":
            content = render.closed()
        elif state == "showResp":
            content = clkq.showResponses(tally)
        elif state == "showAns":
            content = clkq.showCorrect()

        selections = gradebook.getStudentSelections(student,sess,page)#makes sure student is shown responses in case of reload
        return render.question(mathpre,content,page+1,state,selections)#added +1 to page for niceness
        
class Comet:
    def GET(self):
        #Take an argument and return a new state. If the state is old then don't return anything. The client also has to loop to request a new state.
        username = validateUser()
        wi = web.input()
        state=wi.state
        page=int(wi.page)-1
        interval = 1
        count = 0
        cycles = 5
        curpage = control.getUserPage(username)

        if not page == curpage:
            return "reload"

        if state.isdigit():#ultimatum timer is on
            sleep(interval)
            return control.giveTimeLeft(username)
        
        for i in range(cycles):#checks every second for changes
            curstate = control.getUserState(username)
            if not state == curstate:
                if curstate == "ultimatum":
                    return control.giveTimeLeft(username)
                else:
                    return curstate
            else:
                sleep(interval)

        if curstate == "ultimatum":
            #returns the number of seconds remaining
            return control.giveTimeLeft(username)
        else:
            return curstate

class submit:
    def GET(self,choice):
        """
        The student sends the answer choice as a url. 
        The figures out what to pass to the toggleChoice method 
        and returns the entry in the daabase (either 0 or 1).
        """
        user = validateStudent()#this is potentially sensitive
        session = control.getStudentSession(user)
        qnumber = control.getSessionPage(session)
        state = control.getStudentState(user)
        if state == "open" or state == "ultimatum":
            return gradebook.toggleChoice(user,session,qnumber,choice)
        else:
            return "-1"
        

class logout:
    """
    Gets rid of cookie, i.e. logs out.
    """
    def GET(self):
        wi = web.input()
        if "msg" in wi:
            status=wi["msg"]
        else:
            status = "logout" 
        web.setcookie('clicker-username','',expires=-1)
        
        raise web.seeother("/?msg="+status)
        #return "Login cookie deleted"

class manage:
    def GET(self):
        validateInstructor()
        instr = getUsername()
        allsections = control.getSections()
        print allsections
        for i in allsections:#repopulate section list in case of roster change
            control.addSection(i)
        allsections.sort()
        yoursections = control.getInstrSections(instr)
        formguts = []
        for i in allsections:
            insec = (i in yoursections)
            entry = form.Checkbox(name=i,value="1",checked=insec)
            formguts.append(entry)
        butt = form.Button(name="button", type="submit", value="Select sections")
        formguts.append(butt)
        f = form.Form(*formguts) #asterisk passes entries as arguments
        return render.manage(bootpre,f)

    def POST(self):
        #debug:
        validateInstructor()
        instr = getUsername()
        wi = web.input()
        allsections = control.getSections()
        selection=[]

        for i in wi:
            if i in allsections:
                selection.append(i)

        for j in allsections:
            if j in selection:            
                control.assignInstructor(instr,j)
            else:
                control.assignInstructor("",j)

        raise web.seeother('/instructor/')

class assign:
    def POST(self):
        instr=validateInstructor()
        #instr = getUsername()
        wi = web.input()
        qid=wi['quiz']
        yoursections = control.getInstrSections(instr)

        #get all entries set up in the database
        for i in wi:
            if i in yoursections:
                sesname = instr+i+qid
                control.assignSession(sesname,i)#assigns session
                gradebook.makeSession(sesname,qid)#initializes gradebook
                control.sessionAdd(sesname)
                students = control.getStudentsBySec(i)
                for j in students:
                    gradebook.addStudent(j,sesname)
        print yoursections
        print qid
        formguts = []
        for i in yoursections: #produce form
            sesname = instr+i+qid
            already = (control.getAssignedQuiz(i) == sesname)
            entry = form.Checkbox(name = i, value="1", checked=already)
            formguts.append(entry)
            butt = form.Button(name="Assign "+qid, type="submit", value="Assign quiz")
        formguts.append(butt)
        f = form.Form(*formguts)
        return render.assign(bootpre,qid,f) #to be completed

    def GET(self):
        return "bar"
    
class addQuiz:
    def POST(self):
        validateInstructor()
        i = web.input()
        newquiz = i['newquiz']
        questions.addQuiz(newquiz)
        raise web.seeother('/assemble/')
        
class preview:
    def POST(self):
        validateInstructor()
        i = web.input()
        quiz = i['quiz']
        newqlist = i['quizlist']
        newqlist = cleanCSL(newqlist)        
        questions.setQuizQuestions(quiz,newqlist)
        hits = questions.getQblocks(quiz)
        hits = map(cq.clkrQuestion,hits)
        return render.assemble(mathpre,quiz,hits,newqlist)
#        return render.bootstrap(prev)

class viewQuestion:
    def GET(self):
        wi = web.input()
        return str(wi)

class assemble:#no argument means start a new quiz
    def GET(self):
        validateInstructor()
        username = getUsername()
        i = web.input()
        if not 'quiz' in i:
            qlist = questions.getQuizzes()
            return render.quizChoser(username,qlist)
        else:
            quizlist = questions.getQuizQuestions(i['quiz'])
            return render.assemble(mathpre,i['quiz'],[],quizlist)
#            return render.bootstrap(body)

    def POST(self):
        validateInstructor()
        i=web.input()
        tag = i['tag']
        quiz = i['quiz']
        newqlist = i['quizlist']
        newqlist = newqlist.replace(' ','')
        questions.setQuizQuestions(quiz,newqlist)
        quizlist = questions.getQuizQuestions(i['quiz'])
        hits = questions.getWithTag(tag)
        qresults = map(cq.clkrQuestion,hits)
        return render.assemble(mathpre,quiz,qresults,quizlist)


class instructor:
    def GET(self):
        name = validateInstructor()
        preamble = render.bootPreamble()
        return render.instructor(preamble,name)
        

class sessions:
    def GET(self):
        username = validateInstructor()
        yoursession = str(control.getInstrSession(username))
        yoursections = control.getInstrSections(username)
        sessdic = {}
        for i in yoursections:
            sessdic[i] = str(control.getAssignedQuiz(i))
        return render.sessions(bootpre,yoursession,sessdic)

class conduct:
    """
    Displays the page that the instructor uses to conduct the
    quiz.
    """
    def GET(self,session):
        username = validateInstructor()
        control.setInstrSession(username,session)
        page = control.getSessionPage(session)
        length = control.getSessionLength(session)
        clkq = questions.giveClickerQuestion(session,page)
        state = control.getSessionState(session)
        return render.ask(mathpre,clkq.renderInstructor(),page+1,length,state)

    def POST(self,action):
        """
        Enables the instructor to control the progress of the quiz
        """
        username = validateInstructor()
        sess = control.getInstrSession(username)
        page = control.getSessionPage(sess)
        length = control.getSessionLength(sess)
        clkq = questions.giveClickerQuestion(sess,page)
        state = control.getSessionState(sess)
        
        if action == "next":
            another = control.advanceSession(sess)
            if another:
                raise web.seeother("/conduct/"+sess)
            else:
                return "<a href=\"/\">quiz finished</a>"

        elif action == "answers":
            return render.ask(mathpre,clkq.showCorrect(),page+1,length,state)

        elif action =="scores":
            tally = gradebook.tallyAnswers(sess,page)
            return render.ask(mathpre,clkq.showResponses(tally),page+1,length,state)

        elif (action == "closed") or (action == "open"):
            control.setSessionState(sess,action)
            raise web.seeother("/conduct/"+sess)

        elif action == "showAns":
            control.setSessionState(sess,action)
            return render.ask(mathpre,clkq.showCorrect(),page+1,length,state)

        elif action == "showResp":
            control.setSessionState(sess,action)
            tally = gradebook.tallyAnswers(sess,page)
            return render.ask(mathpre,clkq.showResponses(tally),page+1,length,state)
        
        return action #for debugging
    


class databases:
    def GET(self):
        validateInstructor()
        grades=csvsql.getTables("gradebook.db")
        grades.remove("sessions") #sessions is not a gradebook 
        return render.databases(bootpre,grades)

class dbview:
    def GET(self,table):
        validateInstructor()
        if table in rosters:
            rdr = csvsql.sqlite3TableToIter(*rosters[table])
        else:
            rdr = csvsql.sqlite3TableToIter("gradebook.db",table)
        return render.bootstrap(table,render.tableDisplay(rdr))

class download:
    def GET(self,request):
        validateInstructor()
        if request == "qbank":
            output = questions.questionsToTexStr()
        elif request in rosters:
            output = csvsql.sqlite3toCSVstring(*rosters[request])
        else: #gradebook requested
            output = csvsql.sqlite3toCSVstring("gradebook.db",request)
        return output

class clearPass:
    def GET(self):
        """
        Allows the instructor to delete student's passwords.
        """
        username = validateInstructor()
        stulist = control.getSessionStudents(username)
        return render.clearPass(bootpre,stulist)

    def POST(self):
        username = validateInstructor()
        stulist = control.getSessionStudents(username)
        wi = web.input()
        user = wi["user"]
        control.clearPassword(user)
        return render.clearPass(bootpre,stulist)

class dropPass:
    def GET(self):
        """
        Clears the users password
        """
        user = validateUser()
        control.clearPassword(user)
        raise web.seeother("/logout/?msg=newpass")
    
class upload:
    def GET(self,item):
        validateInstructor()
        return render.upload(bootpre,item)

    def POST(self,item):
        #issue, maybe some confirmation/preview page is in order.
        validateInstructor()
        wi = web.input()
        fstr = wi['upfile']
        if item == 'qbank':
            f = open(questionBankLocation,'w')
            f.write(fstr)
            f.close()
            questions.updateBank(fstr)
            return "File uploaded and database updated. Use the back button"

        if item in rosters:
            db = rosters[item][0]
            table = rosters[item][1]
            csvsql.csvOverwrite(db,table,fstr)
            if item == "students":
                control.populateSections()
            return "File uploaded and database updated. Use the back button"

class uploadImg:
    def GET(self):
        validateInstructor()
        return render.uploadImg(bootpre,None)

    def POST(self):
        validateInstructor()
        wi= web.input()
        fstr = wi['upfile']
        fname = wi['fname']
        target = "static/images/{0}".format(fname)
        f = open(target,'w+')
        f.write(fstr)
        f.close
        return render.uploadImg(bootpre,fname)

class new:
    def GET(self):
        validateInstructor()
        return render.newQuestion(None)

    def POST(self):
        validateInstructor()
        ID = web.input()['ID']
        if questions.isInTable("questionbank","ID",ID):
            return render.newQuestion(ID)
        else:
            raise web.seeother("/edit/?ID={0}".format(ID))
        
class edit:    
    def GET(self):
        ####
        #Require ID if none create
        ####
        username = validateInstructor()
        wi = web.input()
        if not "ID" in wi:
            pclq = pq.Question()
        else:
            bob = questions.getQuestion(wi["ID"])
            pclq = pq.Question()
            if not bob == None:#set it to new clicker question
                clq = cq.clkrQuestion(bob)
                pclq.eatClq(clq)
            pclq.setID(wi["ID"])
        return render.edit(pclq)

    def POST(self):
        wi = web.input()
        pclq = pq.Question()
        action = wi['action']
        ID = wi['ID']
        pclq.setID(ID)
        pclq.eatTagStr(wi['tags'])
        pclq.setStatement(wi['stmt'])
        #print wi.keys()

        keyz = wi.keys()
        subchoices = []
        for i in keyz:
            if i[:len(i)-1]==ID: subchoices.append(i)
        # bob = questions.getQuestion(ID)
        # clq = cq.clkrQuestion(bob)
        correct = []
        for i in subchoices:
            pclq.choices[i]=wi[i]
            if i+"-checked" in wi:
                correct.append(i)
        pclq.setAnswers(correct)
        
        
        if action == "addchoice":
            pclq.addChoice()
            questions.updateQuestion(ID,wi['tags'],pclq.writeQblock())
            raise web.seeother("/edit/?ID={0}".format(ID))
        elif action == "remove":
            pclq.rmChoice()
            questions.updateQuestion(ID,wi['tags'],pclq.writeQblock())
            raise web.seeother("/edit/?ID={0}".format(ID))
        elif action == "save":
            questions.updateQuestion(ID,wi['tags'],pclq.writeQblock())
            raise web.seeother("/edit/?ID={0}".format(ID))
        elif action == "preview":
            content = pclq.barfClq().showCorrect()
            return render.question(mathpre,content,0,"open",[])
        else:
            raise web.seeother("/")
            
#Rock and Roll!
if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()

