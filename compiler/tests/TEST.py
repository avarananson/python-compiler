
import os
os.system('python test1.py > o')
os.system('python ../main.py test1.an -sim > o1')
os.system('python ../main.py test1.an -compile > o2')
print(open('o','r').read() == open('o1','r').read() == open('o2','r').read())
