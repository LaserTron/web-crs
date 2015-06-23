import web
import control
import gradebook
#from control import *
from time import sleep
#import question
from question import getQuestion

urls = (#this delcares which url is activated by which class
    '/', 'index',
    '/comet/(.+)', 'Comet',
    '/quiz/(.+)','question',
    '/submit/(.+)', 'submit'
)

render = web.template.render('templates/')

class index:
    def GET(self):
        username=web.cookies().get('clicker-username')
        if username == None:
            return render.login()
        else:
            quizurl='/quiz/{0}'.format(username)
            raise web.seeother(quizurl)
            
    def POST(self):
        i = web.input()
        #return(str(i))
        username=i.username
        control.addUser(username,'Test')#This is just for prototype purposes
        gradebook.addStudent(username,'Test')
        web.setcookie('clicker-username', username)
        quizurl='/quiz/{0}'.format(username)
        raise web.seeother(quizurl)


class question:
    def GET(self,username):
        Qspecs = getQuestion(username)
        return render.question(Qspecs)

    # def POST(self,answers):
    # #webid is a dictionary, you can loop over the keys
    #     return("yay")
    #     # student = web.cookies().get('clicker-username')
    #     # if student == None: #if for some reason the cookie is unset
    #     #     raise web.seeother('/')
    #     # answers = web.input()
    #     # for entry in answers:
    #     #     gradebook.setAnswer(student,entry,answers[entry])
    #     # return("yay")
            
class Comet:
    def GET(self,state):
        #idea make this take an argument and return a new state. If the state is old then don't return anything. The client also has to loop.
        interval = 1
        count = 0
        cycles = 5
        for i in range(cycles):
            curstate = control.getState('index')
            if not state ==  curstate:
                return curstate
            else:
                sleep(interval)
        return curstate

class submit:#this is to submit answers
    def GET(self,state):
        student=web.cookies().get('clicker-username')
        if student == None:
            return render.login() 
        stateli = state.split('/XXX/')
        print stateli
        entered = stateli[0]
        entered = entered.split("/")
        if u"" in entered: entered.remove(u"")
        print entered
        nonentered = stateli[1]
        nonentered = nonentered.split("/")
        if u"" in nonentered: nonentered.remove(u"")
        print nonentered
        for i in entered:
            gradebook.setAnswer(student,i,1)
        for i in nonentered:
            gradebook.setAnswer(student,i,0)
        return "Server reports the following are entered: "+str(entered)
    
#Rock and Roll!
if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()

