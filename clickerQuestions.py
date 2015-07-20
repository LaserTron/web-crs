#
#will require a question database 
#This module contains the clkrQuestion class, which interprets qblocks,
#and renders itself as html
#
#Also contains methods for getting tex files into the database
#

import re
from string import join
from questions import *
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

def noComments(q):#removes latex comments
    lines = q.split('\n')
    pat = re.compile('[^\\\\]%.*')
    output = []
    for l in lines:
        output.append(pat.sub('',l))
    return join(output,'\n')

def getEnvironments(en,s):#extacts question blocks from a .tex file
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
    
def deBrace(s):#removes enclosing braces
    return s.strip("{}")

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

        self.content = noComments(qblock)
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
        return output
        
    def addToDb(self):
        addQuestion(self.ID, self.tagStr, self.content)

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

def loadBank():
    output = []
    qbank = dumpFileToString(banklocation)
    qus = extractQuestions(qbank)
    for qblock in qus:
        output.append(clkrQuestion(qblock))
    return output

def populateBank():
    qus = loadBank()
    for i in qus:
        i.addToDb()

def rePopulateBank():
    clearQuestions()
    populateBank()

