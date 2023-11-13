import os
print('========================================================================')
os.system('python test_binary.py > o')
os.system('python ../main.py test_binary.an -sim > o1')
os.system('python ../main.py test_binary.an -compile > o2')
print('Testing binary ops -> ',open('o','r').read() == open('o1','r').read() == open('o2','r').read())


os.system('python test_relational_equality.py > o')
os.system('python ../main.py test_relational_equality.an -sim > o1')
os.system('python ../main.py test_relational_equality.an -compile > o2')
print('Testing relational equality ops -> ', open('o','r').read() == open('o1','r').read() == open('o2','r').read())

os.system('python test_logical.py > o')
os.system('python ../main.py test_logical.an -sim > o1')
os.system('python ../main.py test_logical.an -compile > o2')
print('Testing logical equality ops -> ', open('o','r').read() == open('o1','r').read() == open('o2','r').read())

os.remove('hello')
os.remove('hello.o')
os.remove('o')
os.remove('o1')
os.remove('o2')
os.remove('compile.asm')
print('========================================================================')
