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

##Upcoming features:
* Flexible flow enabling Mazur's Peer Instruction tehcnique, e.g. the option to only show students the response rates (but not the correct answer) and the option to ask a question again without revealing the answer after student deliberation.
* A countdown timer.
* Encryption, i.e. https.
* Web-based question composer/editor interface so that the user can compose questions without knowing latex.

##Required packages (Linux):
* `python2`
* `sqlite3`
* `sqlitestudio` (recommended)

##Required python modules:
* `web.py` (installable via python 2 `easy_install`)

##How to get it running:
Download the directory, ensure the required packages and python 2 modules are installed, cd into the directory  and type: `python2 webcrs.py`. You can also add an optional port as an argment e.g. `python2 webcrs.py 1234`, for port 80 you'll need privileges.

Connect by pointing your browsers to the host's ip address (at the default port 8080) e.g. type something like `192.168.0.103:8080` into your browser url bar. To log in as an instructor use the username `prof`. There is already a section called `test1` with students `alice, bob, charlie, dylan, eve`. 

Go to the manage database page and download the question bank. With any latex knowledge you should figure out how to compose your own question. Using the upload link you can overwrite the old questionbank with your own questions. Similarly you can also overwrite the instructor and student rosters with your own.

##Which technologies are used?
* HTML 5
* bootstrap
* MathJax
* python 2
* web.py
* sqlite3

##Apologies
I am an amateur programmer and started this project knowing only some python. I learned everything else as I was writing this program, consequently some bits may be a bit sloppy and some refactoring is definitely in order. To get rid of certain things like old gradebooks or student sections the databases may have to be edited directly.

Updated: July 27
