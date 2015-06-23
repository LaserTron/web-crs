Tit="Q1"
Qstmt= "We know $V(r) = 4/3 \pi r^3$, where $r$ is the radius in inches and $V(r)$ is in cubic inches.  The expression represents $$ \\frac{V(3)-V(1)}{3-1} $$"

a1=["The average rate of change of the volume with respect to the radius when the radius changes from 1 inch to 3 inches.","MS1A",False]
a2=["The average rate of change of the radius with respect to the volume when the volume changes from 1 cubic inch to 3 cubic inches.","MS1B",False]
a3=["The average rate of change of the radius with respect to the volume when the radius changes from 1 inch to 3 inches.","MS1C",True]
a4=["The average rate of change of the volume with respect to the radius when the volume changes from 1 cubic inch to 3 inches.","MS1D",False]

def getQuestion(dummy):
    output = [Tit,Qstmt,[a1,a2,a3,a4]]
    return output
