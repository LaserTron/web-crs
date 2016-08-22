#!/usr/bin/env python
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
# This block is to get HTTPS going.
# The instruction  http://webpy.org/cookbook/ssl do not work, 
# but following the instructions
# http://www.8bitavenue.com/2015/05/webpy-ssl-support/
# works. You may uncomment the three commands below this to get ssl, but you
# still need a certifying authority.
#############
# from web.wsgiserver import CherryPyWSGIServer
# CherryPyWSGIServer.ssl_certificate = "server.crt"
# CherryPyWSGIServer.ssl_private_key = "server.key"
# ############
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
    '/direct/','direct', #This is for when credentials are provided in web-input
    '/comet/', 'Comet',
    '/quiz/','question',
    '/conduct/','conduct',
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
    '/setTimer/','setTimer',
    '/viewQuestion/','viewQuestion',
    '/uploadImg/','uploadImg',
    '/populatePassHash','pph'
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
            destination = '/quiz/'#{0}'.format(username) DO WE REALLY NEED TO DISPLAY THE USERNAME?
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

class direct:
    def POST(self):#modified to avoid sending user ids over the internet
        wi = web.input()
        #username = wi["user"]
        passhash = wi["passhash"]
        username = control.getEntry("students","username","password",passhash)
        if username == None:#i.e. it's an isntructor
            username = control.getEntry("instructors","username","password",passhash)
        web.setcookie('clicker-username', username)
        web.setcookie('clicker-passhash', passhash)
        raise web.seeother("/")
        
    
class question:
    def GET(self):#,username):
        student = validateStudent()#ensures credentials are okay
        username = student
        #if not student==username:
        #    raise web.seeother("/logout/?msg=unauthorized")
        sess = control.getStudentSession(username)
        page = control.getSessionPage(sess)
        if page == None:
            return render.studentFinished()
        state = control.getSessionState(sess)
        if state == "finished":
            return render.studentFinished() 
        tally = gradebook.tallyAnswers(sess,page)
        clkq = questions.giveClickerQuestion(sess,page)

        #STATE SWITCH
        if state == "init":
            content = render.notReady()
            title = "Get ready"
        elif state == "open" or state =="ultimatum":
            title="Question"
            content = clkq.getRendered()
        elif state == "closed":
            title = "Question closed"
            content = clkq.getRendered()
        elif state == "showResp":
            title = "Class responses"
            content = clkq.showResponses(tally)
        elif state == "showAns":
            title = "Correct answer"
            content = clkq.showCorrect()

        selections = gradebook.getStudentSelections(student,sess,page)#makes sure student is shown responses in case of reload
        if state == "closed":
            return render.questionClosed(mathpre,title,content,page+1,state,selections)
        else:
            return render.question(mathpre,title,content,page+1,state,selections)
        
class Comet:
    def GET(self):
        """
        The purpose of this method is to keep a variable called
        state synchronized in real time bewtween the  client and 
        what is recorded on the database. See the file 
        /static/control.js for the client-side code that goes 
        with this.
        """
        username = validateUser()
        wi = web.input()
        state=wi.state
        page=int(wi.page)-1
        interval = 1
        count = 0
        cycles = 5
        curpage = control.getUserPage(username)
        systate = control.getUserState(username)
        print "Client STATE:"+state#debug
        print "Server STATE:"+systate

        if not page == curpage:
            return "reload"

        if state.isdigit() and systate == "ultimatum":#ultimatum timer is on
            sleep(2*interval)
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
            #else:
                #control.assignInstructor("",j)
            #this bug prevents multiple instructors
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


class viewQuestion:
    def GET(self):
        wi = web.input()
        ID=wi['ID']
        #return ID
        ID = str(ID)
        qblk = questions.getQuestion(ID)
        if qblk == None:
            return "Question not found. Did you save yet?"
        clq = cq.clkrQuestion(qblk)
        content = clq.showCorrect()
        pre = str(mathpre)+"\n<link href=\"/static/question.css\" rel=\"stylesheet\">"
        return render.bootstrap(pre,"Preview",content)


class assemble:#no argument means start a new quiz
    def GET(self):
        validateInstructor()
        username = getUsername()
        #return username
        i = web.input()
        if not 'quiz' in i:
            qlist = questions.getQuizzes()
            return render.quizChoser(username,qlist)
        else:
            quizlist = questions.getQuizQuestions(i['quiz'])
            return render.assemble(mathpre,i['quiz'],[],quizlist)


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
    def GET(self):
        username = validateInstructor()
        wi = web.input()
        #return str(wi)
        action = wi['action']
        if action == "setsession":
            sess = wi['session']
            control.setInstrSession(username,sess)
        session = control.getUserSession(username)
        sess=session #lazyness
        page = control.getSessionPage(session)
        length = control.getQuizLength(session)
        clkq = questions.giveClickerQuestion(session,page)
        state = control.getSessionState(session)
        print str(wi) #debug

        ###############
        # Issue:
        # There is a strange bug that the correct pages aren't always 
        # served. E.g. click on "next" but the url indicates another
        # action. This is annoying, but I don't know how to fix it.
        # For now, however, here is a clause that pervents
        # immediately showing the answers or skipping to the next
        # answer. The fix seems to work but buttons don't work very well
        #################

        ####
        # Weird redirect bug fix, to pervent passing to next,
        # showAns, showResp.
        ###
        if (state == "init" or state == "ultimatum" or state=="open"):blocked=True
        else: blocked=False
        
        if action == "setsession":
            return render.ask(mathpre,clkq.showCorrect(),page+1,length,state)        
        elif action == "next":
            #if blocked:#bypass
            #    return render.ask(mathpre,clkq.showCorrect(),page+1,length,state) 
            state = "init"
            another = control.advanceSession(session)
            page = page+1 #To ensure that the correct page is displayed
            clkq = questions.giveClickerQuestion(session,page)#update clickerquestion to be displayed
            if another:
                return render.ask(mathpre,clkq.showCorrect(),page+1,length,state)        
            else:
                return "<a href=\"/\">quiz finished</a>"

        elif action == "answers":
            return render.ask(mathpre,clkq.showCorrect(),page+1,length,state)

        elif action =="scores":
            tally = gradebook.tallyAnswers(sess,page)
            return render.ask(mathpre,clkq.showResponses(tally),page+1,length,state)

        elif (action == "closed") or (action == "open"):
            #print "ACTION:"+action#debug
            #return str(wi)
            control.setSessionState(sess,action)
            state = action
            return render.ask(mathpre,clkq.showCorrect(),page+1,length,state)        

        elif action == "showAns":
            if blocked:#bypass
                return render.ask(mathpre,clkq.showCorrect(),page+1,length,state) 
            control.setSessionState(sess,action)
            print "Return answers"
            return render.ask(mathpre,clkq.showCorrect(),page+1,length,state)

        elif action == "showResp":
            if blocked:#bypass
                return render.ask(mathpre,clkq.showCorrect(),page+1,length,state) 
            control.setSessionState(sess,action)
            tally = gradebook.tallyAnswers(sess,page)
            print "retrun tally"
            return render.ask(mathpre,clkq.showResponses(tally),page+1,length,state)
        
        return "gurgle"


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
        return render.bootstrap(bootpre,table,render.tableDisplay(rdr))

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
            questions.updateBank(fstr)
            return "Questionbank updated, no questions overwritten."
            #     f = open(questionBankLocation,'w')
            #     f.write(fstr)
            #     f.close()
            #     questions.updateBank(fstr)
            #     return "File uploaded and database updated. Use the back button"
        
        
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
        return render.upImgSuccess(bootpre,fname)

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
            pclq.addChoice()
        else:
            bob = questions.getQuestion(wi["ID"])
            pclq = pq.Question()
            pclq.setID(wi["ID"])
            if not bob == None:#set it to new clicker question
                clq = cq.clkrQuestion(bob)
                pclq.eatClq(clq)
            else:
                pclq.addChoice()
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
        # elif action == "preview":
        #     content = pclq.barfClq().showCorrect()
        #     return render.question(mathpre,content,0,"open",[])
        else:
            raise web.seeother("/")

class setTimer:
    def GET(self):
        username = validateInstructor()
        t=web.input()['time']
        control.setUltimatum(username,int(t))

class pph:
    """
    This is just a quick an dirty method to invoke control.populatePassHash
    """
    def GET(self):
        validateInstructor()
        control.populatePassHash()
        raise web.seeother("/instructor/")
#Rock and Roll!
if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()

