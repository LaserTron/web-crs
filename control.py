import web

#
#Requires a DB with a table called 'States' with columns 'state' and 'page'
#Requires a DB with a tabe called 'Users' with columns 'username' and 'section'

ctrl = web.database(dbn="sqlite",db="control.db")

def isInTable(table,col,entry):
    wherestring = '{0}=\"{1}\"'.format(col,entry)
    res = ctrl.select(table,where=wherestring)
    return bool(res)

def getState(page):
    wherestring = "page=\"{0}\"".format(page)
    bob=ctrl.select("States", where=wherestring, what='state')
    return bob[0]['state']
    
def setState(page,st):
    wherestring = "page=\"{0}\"".format(page)
    ctrl.update("States", where=wherestring, state=st)
    
def addUser(user,sec):
    user=user.strip()
    res = isInTable('Users','username', user)
    if not res:#no user there
        ctrl.insert('Users',username = user, section = sec)

def getUserSection(user):
    wherestring="username=\"{0}\"".format(user)
    bob=ctrl.select('Users', where=wherestring, what='section')
    return bob[0]['section']

def delUser(user):
    wherestring="username=\"{0}\"".format(user)
    ctrl.delete('Users',where=wherestring)
