"""
This module is supposed to represent a LaTex-free question 
"""
import cPickle as pkl
import cStringIO as csi
import clickerQuestions as cq

def objToStr(obj):
    """
    Pickles an object to a string
    """
    inio =csi.StringIO()
    pkl.dump(obj,inio)
    inio.seek(0)
    return inio.read()

def strToObj(s):
    "Takes a pickle string and returns the object"
    wrio =csi.StringIO()
    wrio.write(s)
    wrio.seek(0)
    return pkl.load(wrio)
    
class Question:
    """
    A more abstract Question class, useful for constructing from form
    data.
    """
    #choices should have keys not involving the ID, but only letters.
    def __init__(self):
        self.ID = ""
        self.tags = []
        self.statement = ""
        self.choices = {}
        self.correct = []
        self.explanation = ""
        
    def getID(self):
        return self.ID

    def setID(self,ID):
        self.ID=ID
    
    def getTagStr(self):
        return ",".join(self.tags)

    def eatTagStr(self,s):
        "Takes comma separated string to list"
        li = s.split(",")
        li = map(lambda x: x.strip(),li)
        self.tags=li
        
    def getStatement(self):
        return self.statement

    def setStatement(self,stmt):
        self.statement = stmt

    def getChoices(self):
        return self.choices

    def addChoice(self):
        zero=ord('A')
        l = zero+len(self.choices)
        ell = chr(l)
        self.choices[self.ID+ell]=""

    def rmChoice(self):
        "Delete last answer choice"
        choices = self.choices.keys()
        choices.sort()
        lastkey = choices.pop()
        self.choices.pop(lastkey)
        if lastkey in self.correct: self.correct.remove(lastkey)
        
    def setChoice(self,ch,content):
        self.choices[ch]="content"

    def setAnswers(self,li):
        self.correct=li

    def writeChoiceRow(self,ans):
        "Writes an html row for the edit template"
        checked = ""

        if ans in self.correct:
            checked = "checked"

        row="<tr><td>{0}</td><td><textarea name=\"{0}\" rows=\"2\" cols=\"60\">{1}</textarea></td><td><input name=\"{0}-checked\" type=\"checkbox\" {2}></td></tr>"
        return row.format(ans,self.choices[ans],checked)
            
    def writeQblock(self):
        template = """\\begin{{clkrQuestion}}{{{0}}}{{{1}}}
{2}
\\begin{{enumerate}}[A.]
{3}
\\end{{enumerate}}
\\answer{{{4}}}
\\explanation{{{5}}}
\\end{{clkrQuestion}}
"""

        tagstr = ",".join(self.tags)

        choicestr=""
        ch =[]
        for i in self.choices: ch.append(i)
        ch.sort()
        for i in ch:
            choicestr += "\\item\\label{{{0}}}{1}\r\n".format(i,self.choices[i])
        ansstr = ",".join(self.correct)
            
        return template.format(self.ID,tagstr,self.statement,choicestr,ansstr,self.explanation)

    def eatClq(self,clq):
        self.ID = clq.ID
        self.tags = map(lambda x: x.strip(),clq.tagStr.split(","))
        self.statement = clq.qstmt
        self.choices = clq.getChoiceDict()
        self.correct = clq.getAnswers()
        self.explanation = clq.explStr
        
    def barfClq(self):
        "produces a clickerquestion, not very elegantly though"
        return cq.clkrQuestion(self.writeQblock())
        
        
