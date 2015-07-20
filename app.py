import web
import control
import gradebook
from time import sleep
from web import form
#from question import getQuestion #for testing
import questions
import clickerQuestions as cq


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
#Notes:
#############
#
# Some sort of validation function is needed to prevent
# impersonation attacks
# 
#############

urls = (#this delcares which url is activated by which class
    '/', 'index',
    '/comet/', 'Comet',
    '/quiz/(.+)','question',
    '/conduct/(.+)','conduct',
    '/submit/(.+)', 'submit',
    '/addQuiz/', 'addQuiz',
    '/compose/' , 'compose',
    '/preview/','preview',
    '/instructor/', 'instructor',
    '/logout', 'logout',
    '/manage/', 'manage',
    '/assign/', 'assign',
    '/sessions/', 'sessions',
    '/prog/(.+)','progress'
)

render = web.template.render('templates/')

def getUsername():
    username=web.cookies().get('clicker-username')
    if username == None:
        return render.login()
    else:
        return username

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
            return render.login()

        if control.isInTable('instructors','username',username):
            destination = '/instructor/'
        elif control.isInTable('students','username',username):
            destination = '/quiz/{0}'.format(username)
        else:
            return username +' not found'#render.login()#TODO add error message!
        raise web.seeother(destination)
            
    def POST(self):
        i = web.input()
        username=i.username
        web.setcookie('clicker-username', username)
        raise web.seeother("/")


class question:
    def GET(self,username):
        sess = control.getStudentSession(username)
        page = control.getSessionPage(sess)
        state = control.getSessionState(sess)
        if state == "finished":
            return render.studentFinished()
        clkq = questions.giveClickerQuestion(sess,page)
        content = render.qTemplate(clkq)
        return render.question(content,page+1,state)#added +1 to page for niceness
        
class Comet:
    def GET(self):
        #idea make this take an argument and return a new state. If the state is old then don't return anything. The client also has to loop.
        username = getUsername()
        wi = web.input()
        state=wi.state
        page=int(wi.page)-1
        interval = 1
        count = 0
        cycles = 5
        curpage = control.getStudentPage(username)
        if not page == curpage:
            return "reload"
        
        for i in range(cycles):
            curstate = control.getStudentState(username)
            if not state ==  curstate:
                return curstate
            else:
                sleep(interval)
        return curstate

class submit:
    def GET(self,choice):
        """
        The user sends the answer choice as a url. 
        The figures out what to pass to the toggleChoice method 
        and returns the entry in the daabase (either 0 or 1).
        """
        user = getUsername()
        session = control.getStudentSession(user)
        qnumber = control.getSessionPage(session)
        return gradebook.toggleChoice(user,session,qnumber,choice)
    
# class submit:#this is to submit answers
#     def GET(self,state):
#         student=web.cookies().get('clicker-username')
#         if student == None:
#             return render.login() 
#         stateli = state.split('/XXX/')
#         print stateli
#         entered = stateli[0]
#         entered = entered.split("/")
#         if u"" in entered: entered.remove(u"")
#         print entered
#         nonentered = stateli[1]
#         nonentered = nonentered.split("/")
#         if u"" in nonentered: nonentered.remove(u"")
#         print nonentered
#         for i in entered:
#             gradebook.setAnswer(student,i,1)
#         for i in nonentered:
#             gradebook.setAnswer(student,i,0)
#         return "Server reports the following are entered: "+str(entered)

class logout:
    """
    Gets rid of cookie, i.e. logs out.
    """
    def GET(self):
        web.setcookie('clicker-username','',expires=-1)
        return "Login cookie deleted"

class manage:
    def GET(self):
        instr = getUsername()
        allsections = control.getSections()
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
        return render.manage(f)

    def POST(self):
        #debug:
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
        instr = getUsername()
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
        return render.assign(qid,f) #to be completed

    def GET(self):
        return "bar"
    
class addQuiz:
    def POST(self):
        i = web.input()
        newquiz = i['newquiz']
        questions.addQuiz(newquiz)
        raise web.seeother('/compose/')
        
class preview:
    def POST(self):
        i = web.input()
        quiz = i['quiz']
        newqlist = i['quizlist']
        newqlist = cleanCSL(newqlist)        
        questions.setQuizQuestions(quiz,newqlist)
        hits = questions.getQblocks(quiz)
        hits = map(cq.clkrQuestion,hits)
        prev = render.compose(quiz,hits,newqlist)
        return render.bootstrap(prev)
        
class compose:#no argument means start a new quiz
    def GET(self):
        username = getUsername()
        i = web.input()
        if not 'quiz' in i:
            qlist = questions.getQuizzes()
            return render.quizChoser(username,qlist)
        else:
            quizlist = questions.getQuizQuestions(i['quiz'])
            body = render.compose(i['quiz'],[],quizlist)
            return render.bootstrap(body)

    def POST(self):
        i=web.input()
        tag = i['tag']
        quiz = i['quiz']
        newqlist = i['quizlist']
        newqlist = newqlist.replace(' ','')
        questions.setQuizQuestions(quiz,newqlist)
        quizlist = questions.getQuizQuestions(i['quiz'])
        hits = questions.getWithTag(tag)
        qresults = map(cq.clkrQuestion,hits)
        body = render.compose(quiz,qresults,quizlist)
        return render.bootstrap(body)

class instructor:
    def GET(self):
        name=web.cookies().get('clicker-username')
        if name == None:
            return render.login()
        if control.isInTable('instructors','username',name):
            return render.instructor(name)
        else:
            raise web.seeother("/")

class sessions:
    def GET(self):
        username = getUsername()
        yoursession = str(control.getInstrSession(username))
        yoursections = control.getInstrSections(username)
        sessdic = {}
        for i in yoursections:
            sessdic[i] = str(control.getAssignedQuiz(i))
        return render.sessions(yoursession,sessdic)

class conduct:
    """
    Displays the page that the instructor uses to conduct the
    quiz.
    """
    def GET(self,session):
        username = getUsername()
        control.setInstrSession(username,session)
        page = control.getSessionPage(session)
        clkq = questions.giveClickerQuestion(session,page)
        return render.ask(clkq.renderInstructor(),page+1)

    def POST(self,action):
        """
        Enables the instructor to control the progress of the quiz
        """
        username = getUsername()
        sess = control.getInstrSession(username)
        if action == "next":
            another = control.advanceSession(sess)
            if another:
                raise web.seeother("/conduct/"+sess)
            else:
                return "quiz finished"
        elif action =="scores":
            page = control.getSessionPage(sess)
            tally = gradebook.tallyAnswers(sess,page)
            clkq = questions.giveClickerQuestion(sess,page)
            return render.ask(clkq.showResponses(tally),page+1)
        return action
    
# class progress:
#     """
#     Enables the instructor to control the progress of the quiz
#     """
#     def GET(self,action):
#         username = getUsername()
#         sess = control.getInstrSession(username)
#         if action == "next":
#             another = control.advanceSession(sess)
#             if another:
#                 raise web.seeother("/conduct/"+sess)
#             else:
#                 return "quiz finished"
#         elif action =="scores":
#             page = control.getSessionPage(sess)
#             tally = gradebook.tallyAnswers(sess,page)
#         return action
    
    
    
#Rock and Roll!
if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()

