#
# will require a question database 
# This module contains the clkrQuestion class, which interprets qblocks,
# and renders itself as html
#
# Also contains methods for parsing tex files and inserting
# questions into a database
#

import re
from string import join
import questions as qu
import web
render = web.template.render('templates/')

banklocation = 'questions/questionbank.tex'

def cleanCSL(csl):
    """
    Takes a string representing a comma separated list and removes spaces and trailing colons
    """
    csl = csl.replace(' ','')
    return csl.strip(',')

def sstrip(s):
    return s.strip()

def openFile(filename):
    f = open(filename,'r')
    return f

def dumpFileToString(filename):
    f=openFile(filename)
    content = f.read()
    f.close()
    return content

def noComments(q):
    "removes latex comments"
    lines = q.split('\n')
    pat = re.compile('[^\\\\]%.*')
    output = []
    for l in lines:
        output.append(pat.sub('',l))
    return join(output,'\n')

def getEnvironments(en,s):
    "Extacts question blocks from a .tex file"
    restring = '\\\\begin\\{{{0}\\}}[\\d\\D]*?\\\\end\\{{{0}\\}}'.format(en)
    pat = re.compile(restring)
    return pat.findall(s)
    
def extractQuestions(bk):
    questions = getEnvironments('clkrQuestion',bk)
    return questions

def getBraced(s):
    restring = '\\{.*?\\}'
    pat = re.compile(restring)
    return pat.findall(s)
    
def deBrace(s):
    "removes enclosing braces"
    return s.strip("{}")

def fixGraphics(bk):
    """
    Takes a qblock and replaces latex code for images with html code.
    """
    restring = '\\\\includegraphics.*?\\{.*?\\}'
    pat = re.compile(restring)
    latexImgLines = pat.findall(bk)#all images
    popout = lambda x: deBrace(getBraced(x)[0])
    mkimgline = lambda x: "<div class=\"container\"style=\"text-align:center\"><img src=\"/static/images/{0}\"></div>".format(x)#use css for image
    htmlize = lambda x:mkimgline(popout(x))
    convDic = {}
    for i in latexImgLines:
        convDic[i]=htmlize(i)
    output = bk
    for i in convDic:
        output = output.replace(i,convDic[i])
    output = output.replace("\\begin{center}","")
    output = output.replace("\\end{center}","")
    return output    
    
def getId(q):
    inter = getBraced(q)[1]
    return deBrace(inter)

def getTags(q):
    inter = getBraced(q)[2]
    return deBrace(inter)

def fixChoiceLine(a):
    a=a.rstrip()
    label = getBraced(a)[0]
    label = deBrace(label)
    restring = '\\s*\\\\label\\s*\\{{{0}\\}}\\s*'.format(label)
    pat = re.compile(restring)
    stmt = pat.sub('',a)
    return [label,stmt]
    
def choiceDict(q):#takes an enumerate environment
    liq = q.split('\\item')
    liq.remove(liq[0])
    if liq ==[]:#fixes the no answe choice bug.
        return {}
    lastentry = liq[len(liq)-1]
    lastentry = lastentry.split('\\end{enumerate}')[0]
    liq[len(liq)-1]=lastentry
    output = {}
    for i in liq:
        fixi = fixChoiceLine(i)
        output[fixi[0]]=fixi[1]
    return output

def getChoices(q):
    return noComments(getEnvironments('enumerate',q)[0])

def getQStatement(q):
    output = noComments(q)
    headre = '\\\\begin\\{clkrQuestion\\}\\{.*\\}\\{.*\\}'
    headpat = re.compile(headre)
    output = headpat.sub('',output) #remove head
    tailre = '\\\\begin\\{enumerate\\}[\s\S]*'
    tailpat = re.compile(tailre)
    output = tailpat.sub('',output)
    return output.strip()

def getAnswers(q):
    ansre = '\\\\answer\\{.*\\}'
    anspat = re.compile(ansre)
    ans = anspat.findall(q)
    if len(ans) == 0:
        return ""
    else:
        ans = ans[0]
        return cleanCSL(deBrace(getBraced(ans)[0]))

def getExplanation(q):
    explre = '\\\\explanation\\{.*\\}'
    explpat = re.compile(explre)
    expl = explpat.findall(q)
    if len(expl) == 0:
        return ""
    else:
        expl = expl[0]
        return deBrace(getBraced(expl)[0])    


class clkrQuestion:

    def __init__(self,qblock):

        self.content = fixGraphics(noComments(qblock))#fixgraphics for graphics.
        self.ID = getId(qblock)
        self.tagStr = getTags(qblock)
        self.qstmt = getQStatement(qblock)
        self.choiceStr =  getChoices(qblock)
        self.answerStr =  getAnswers(qblock)
        self.explStr = getExplanation(qblock)
    
    def hasTag(self,tag):
        tags = map(sstrip,self.tagStr.split(','))
        return (tag in tags)
    
    def getChoiceDict(self):
        return choiceDict(self.choiceStr)

    def getChoices(self):
        output = []
        for i in self.getChoiceDict():
            output.append(i)
        output.sort()
        return output
        
    def addToDb(self):
        #qu.addQuestion(*map(unicode,[self.ID, self.tagStr, self.content]))
        qu.addQuestion(self.ID, self.tagStr, self.content)

    def getAnswers(self):
        return map(sstrip,self.answerStr.split(','))

    def checkAnswer(self,choice):
        correct = self.getAnswers()
        return choice in correct
    
    # def getAnswerStr(self):
    #     return self.answerStr
    
    def getTotal(self):
        return len(map(sstrip,self.answerStr.split(',')))

    def getQuestion(self):
        return getQStatement(self.content)

    def getRendered(self):
        return render.qTemplate(self)

    def renderInstructor(self):
        return self.showCorrect()

    def showQuestion(self):
        return self.getRendered()
    
    def showResponses(self,tally):
        return render.respTemplate(self,tally)
    
    def showCorrect(self):
        colordic = self.getChoiceDict()
        correct = self.getAnswers()
        for i in colordic:
            if i in correct:
                colordic[i]="LightGreen"
            else:
                colordic[i]="#FFCCCC"
        return render.ansTemplate(self,colordic)

    def showEdit(self):
        return "This should show the correct answer and a couple buttons."

