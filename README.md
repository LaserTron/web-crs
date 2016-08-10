#Web based classroom response system#
Author: Nicholas Touikan

##What is it?
It is a web application designed for conducting in-class quizzes, i.e. a classroom response system. Originally it is intended for calculus classes and is designed to be run from a personal computer. This program is distributed under the GNU Lesser General Public License.

##Why?
Clickers, which are physical devices, are a fashionnable classroom response technology, however the ubiquity of portable and versatile devices such as smartphones,tablets, and laptops makes them obsolete. Not only does a web application offer more possiblities, it  eliminates the hassle of ensuring that every classroom has properly functionning equipment. Directly displaying quiz questions on student's devices also enables a fluid integration of clicker questions into lecctures and frees up the black/white board for the important stuff.

 My reason for writing this program is so to give instrucors (myself included) complete control of their classroom response system and the features they need.

##Current features:
* Doesn't involve Microsoft PowerPoint.
* The problem bank is written in LaTex and displayed using html 5 and mathjax.
* Problem sets, or quizzes, can be assembled on the fly.
* The student interface is updated dynamically: when the instructor advances to the next question, the new question is automatically loaded on the student's device.
* Student responses are recorded and graded on the fly. Grades can be downloaded as comma separated value file (csv) that is compatible with all known current spreadsheet programs.
* Instructors can instantly see student responses.
* Supports multiple simultaneous instructors and lecture sessions.
* Instructor and student rosters can be downloaded and uploaded/updated via .csv files.
* All users have passwords.
* Image support.
* Live coutdown timer.
* Webased question composer/editor interface so that the user can compose questions conveniently in html + mathjax.

##Upcoming features:
* Flexible flow enabling Mazur's Peer Instruction technique, e.g. the option to only show students the response rates (but not the correct answer) and the option to ask a question again without revealing the answer after student deliberation. (Note this can still be achieved by asking questions twice in a row, and there is an option to skip a question before showing it to students.)
* Encryption, i.e. https.

##Required package:
* `python2`

##Required python module:
* `web.py` (installable via python 2 `easy_install`)

##How to get it running:
Download the directory, ensure the required packages and python 2 module is installed, cd into the directory  and type: `python2 webcrs.py`. You can specify the port as follows `python2 webcrs.py 1234`. For special ports you need special privileges. **Due to web.py's limitations, this program will not work with more than 10 users. See Deployment below**

Connect by pointing your browsers to the host's ip address (at the default port 8080) e.g. type something like `192.168.0.103:8080` into your browser url bar. To log in as an instructor use the username `prof`. There is already a section called `test1` with students `alice, bob, charlie, dylan, eve`. By default the usernames are unset.

Student and instructor rosters can be modified by uploading .csv files in the databases page.

Go to the manage database page and download the question bank. With any latex knowledge you should figure out how to compose your own question. Using the upload link you can update the old questionbank with your own questions. To clear it you will have to edit the database `questions.db` directly.

##Deployment
This webapp was successfully deployed on a [Linode](http://www.linode.com) running Ubuntu 16.04 LTS and served through lighttpd. Here are instructions.

1. Install the packages `git, python-pip, lighttpd`
2. Clone this git repo
3. `pip install webpy`
4. `pip install flup`
5. `chmod +x webcrs.py`
5.  Use the following as `/etc/lighttpd/lighttpd.conf` (copy-pasted from [here](http://webpy.org/deployment) and assuming the repository is located at `/root/web-crs/`.

```
server.modules = ("mod_fastcgi", "mod_rewrite")
server.document-root = "/root/web-crs/"     
fastcgi.server = ( "/webcrs.py" =>
((
   "socket" => "/tmp/fastcgi.socket",
   "bin-path" => "/root/web-crs/webcrs.py",
   "max-procs" => 1,
   "bin-environment" => (
     "REAL_SCRIPT_NAME" => ""
   ),
   "check-local" => "disable"
))
)

mimetype.assign = (".css" => "text/css")

url.rewrite-once = (
   "^/favicon.ico$" => "/static/favicon.ico",
   "^/static/(.*)$" => "/static/$1",
   "^/(.*)$" => "/webcrs.py/$1"
)
```

##Which technologies are used?
* HTML 5
* bootstrap
* MathJax
* python 2
* web.py
* sqlite3

##Apologies
I am an amateur programmer and started this project knowing only some python. I learned everything else as I was writing this program, consequently some bits may be a bit sloppy and some refactoring is definitely in order. To get rid of certain things like old gradebooks or student sections the databases may have to be edited directly.

Updated: August 10 2016
