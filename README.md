#Web based classroom response system#
Author: Nicholas Touikan

##What is it?
It is a web application designed for conducting in-class quizzes, i.e. a classroom response system. Originally it is intended for calculus classes.

##Current features:
*The problem bank is written in LaTex.
*Problem sets, or quizzes, can be assembled on the fly.
*The student interface is updated dynamically: when the instructor advances to the next question, the new question is automatically loaded on the student's device.
*Student responses are recorded on the fly and grades can be downloaded as comma separated value (csv) that are compatible with all spreadsheet programs.
*Instructors can instantly see what the student responses were.
*Supports multiple simultaneous instructors and lecture sessions.
*Instructor and student rosters can be downloaded and uploaded/updated via .csv files.

##Upcoming features:
*Flexible flow enabling Mazur's Peer Instruction tehcnique, e.g. the option to only show students the response rates (but not the correct answer) and the option to ask a question again after student deliberation.
*A countdown timer.
*Support for images.
*https and passwords. (The current version is fundamentally insecure)

##Required packages (Linux):
*`python2`
*`sqlite3`
*`sqlitestudio` (recommended)

##Required python modules:
*`web.py` (installable via python 2 `easy_install`)

##How to get it running:
Download the directory, ensure the required packages and python 2 modules are installed,  and type: `python2 webcrs.py`

To log in as an instructor use the username `prof`. There is already a section called `test1` with students `alice, bob, charlie, dylan, eve`.

Go to the manage database page and download the question bank. With any latex knowledge you should figure out how to compose your own question.

##Which technologies are used?
*HTML 5
*bootstrap
*MathJax
*python 2
*web.py
*sqlite3

##Apologies
I am an amateur programmer and started this project knowing only some python. I learned everything else as I was writing this program, consequently some bits may be a bit sloppy and some refactoring is definitely in order.

Updated: July 23