"""This class provides a way to see results from the gradebook
and to assign grades to students.
"""

import gradebook, questions
#import csvtosqlite3 as csv2sql
import numpy

#from gradebook import gdbk
from dbDump import retrieve
from csvtosqlite3 import sqlite3TableToDictList as sql2dili
from csvtosqlite3 import dictListToCsvString as dl2csvs
from csvtosqlite3 import getTables
from clickerQuestions import clkrQuestion

class Session:
    
    "Essentially a nice wrapper for a table in gradebook.db"
    def __init__(self,sessname,cutoffRate=0.3,cutoffScore=0.2,forgetRatio=4,quorumRatio=0.5):
        """cutoffRate excludes questions that were notmissed by more than that many students.
        cutoffScore exsludes questions that scored below that threshold. forgetRatio
        gives the ratio of questions that may be missed. Quorum is the fraction the 
        of present students needed to include the question."""
        self.sessname=sessname
        db = gradebook.gdbk        
        self.dili = sql2dili(db,sessname)

        self.cutoffRate=cutoffRate
        self.cutoffScore=cutoffScore
        self.forgetRatio=forgetRatio
        
        
        dico={'where':"name=\"{0}\"".format(sessname)}
        qstring = retrieve(db.select("sessions",**dico))["questions"]
        self.qlist = qstring.split(',')

        qblocks = map(questions.getQuestion,self.qlist)
        self.clickerQuestions = map(clkrQuestion,qblocks)

        self.students=map(lambda x:x['username'],self.dili)
        self.totalStudents = len(self.students)

        self.quorum = quorumRatio*self.totalStudents #number of minimal students needed to keep question
        self.hasQuorum = True #assume there are sufficienttly many students
        
        self.length =len(self.qlist)
        self.Qi = []
        for i in range(self.length):
            self.Qi.append("Q"+str(i))

        #Inialize some lists and dictionaries to be populated by methods
        self.present=[]
        self.absent=[]

        self.included = self.Qi[:]#copies the list
        self.averages ={}
        self.rates={}

        for i in self.Qi:
            #self.included[i]=True
            self.averages[i]=None
            self.rates[i]=0
            
        self.scores = {}
        
    def excludeQuestion(self,n):
        """Excludes question Qn"""
        entry = "Q"+str(n)
        self.included.remove(entry)

    def attendance(self):
        """Gets the list entries of absent students and updates the dictionary list."""
        absent = lambda x: len(set(x.values()))==2
        absentees = []
        for i in self.dili:
            if absent(i):
                absentees.append(i)
        self.absent = map(lambda x:x['username'],absentees)
        #list comprehension (not very comprehensible)
        #http://stackoverflow.com/questions/11434599/remove-list-from-list-in-python
        self.present = [student for student in self.students if student not in self.absent]
        self.dili = [records for records in self.dili if records not in absentees]

        #now determine whether to keep the session due to quorum
        self.hasQuorum =  (len(self.present)>self.quorum) #True or false.
        if not self.hasQuorum:
            self.persent = []
            self.dili=[]

    def responseRate(self,n):
        "Computes response rate on question n"
        total = len(self.dili)
        hits = 0.0
        entry = "Q"+str(n)
        for e in self.dili:
            if not e[entry] == None:
                hits = hits+1
        if hits == 0.0:
            return 0.0
        else:
            return hits/total

    def average(self,n):
        "Computes average on question n"
        total = len(self.dili)
        total = total*self.responseRate(n)
        score = 0.0
        entry = "Q"+str(n)+"total"
        for e in self.dili:
            s = e[entry]
            if not s == None:
                score = score+s 
        if score ==0:
            return 0
        else:
            return score/total

    def autoExclude(self,rate=0.3,score=0.2):
        """Excludes certain questions form gradebook"""
        rate = self.cutoffRate
        score = self.cutoffScore
        for i in range(self.length):
            av = self.average(i)
            ra = self.responseRate(i)
            if (av < score) or (ra < rate):
                print """Question {num} excluded.
average: {avg}
response rate:{rate}""".format(num=str(i),avg=av,rate=ra)
                try:
                    self.excludeQuestion(i)
                except ValueError:
                    print "Value error: meh!"

    def compileStats(self):
        """Computes averages, rates, autoexcludes and outputs 
        student scores. If forgetFreq=n, then a student is excused to have forgotten
        approximately 1/n of the answers, so we only keep the highest answers.
        """
        self.attendance()
        forgetRatio = self.forgetRatio
        for i in range(self.length):
            entry = "Q"+str(i)
            av = self.average(i)
            self.averages[entry]=av
            rr = self.responseRate(i)
            self.rates[entry]=rr

        self.autoExclude()
        realLength = len(self.included)
        if not forgetRatio== 0:
            forgettables = realLength/forgetRatio
        else:
            forgettables = 0

        print "Total questions recorded {1}.\nAllowing {0} questions to be missed.".format(forgettables,realLength)

        
        total = (realLength-forgettables)
        weightedScores={}
        for stu in self.dili:#add up the scores
            name = stu['username']
            scores =[]
            for q in self.included:
                entry = stu[q+"total"]
                if entry == None:
                    entry = 0
                    #print "Student {0} forgot to enter question {1}".format(name,q)
                scores.append(entry)
                 
            scores.sort()
            scores = scores[-total:]#keep the total highest
            try:
                score = sum(scores)
            except TypeError:
                print "WHOA:"+str(scores)
                score = 0
            self.scores[name]=score
            weightedScores[name]=score/(total*1.0)
            
        allscores = weightedScores.values()
        try:
            average = sum(allscores)/float(len(allscores))
            median = numpy.median(numpy.array(allscores))
        except ZeroDivisionError:#everything is empty
            print self.sessname + " has no entries."
            average=None
            median=None
        weightedScores['ZZZZAVERAGE']=average
        weightedScores['ZZZZMEDIAN']=median
        return weightedScores #a dictionary with usernames as keys


class masterGradebook:
    
    """The purpose of this class is to produce a csv file from a 
    list of sessions. The master gradebook is a dictionary with 
    usernames as keys and possible grades for each session."""

    def __init__(self,sessionlist):

        self.sessionlist = sessionlist
        self.master = {}
        self.Sessions=[]
        self.rows=[]

    def fillIn(self,cutoffRate=0.3,cutoffScore=0.2,forgetRatio=4,quorumRatio=0.5):
        for sess in self.sessionlist:#go through session list
            ses = Session(sess,cutoffRate=cutoffRate,cutoffScore=cutoffScore,forgetRatio=forgetRatio,quorumRatio=quorumRatio)#makes an instance of Session
            results = ses.compileStats()#returns a dictionary with student scores
            if ses.hasQuorum:
                sessname = ses.sessname#get the name of the session
                for student in results:#goes through dict and inserts in to
                    student=str(student)
                    score =results[student]
                    try:
                        self.master[student][sessname]=score
                    except KeyError:#No dictionary created yet
                        self.master[student]={sessname:score}#initialize dictionary
                self.Sessions.append(ses)
            else: self.sessionlist.remove(sess)#didn't have quorum

                
        self.rows=[]#clear rows
        for s in self.master:
            en = self.master[s]
            attendance = len(en.values())
            en['username']=s
            en['attendance']=attendance

        self.rows = self.master.values()

    def toCsvString(self):
        """Returns a string tha can be written to a csvfile"""
        header = ['username']+self.sessionlist+['attendance']
        return dl2csvs(self.rows,fields=header)

def masterGradebookBySection(sec):
    """Takes the list of sections from gradebook db and returns all sessions
    whose name contains sec as a subword"""
    allsessions = getTables(gradebook.gdbk)
    secsessions = [s for s in allsessions if sec in s]
    m = masterGradebook(secsessions)
    m.fillIn()
    return m

def quickAndDirtyCsv(sec):
    "Gives a .csv file for that section:"
    f = open("{0}.csv".format(sec),'w')
    m = masterGradebookBySection(sec)
    f.write(m.toCsvString())
    f.close()
