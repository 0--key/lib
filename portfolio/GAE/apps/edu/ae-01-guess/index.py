import sys

print 'Content-Type: text/html'
print ''
print '<pre>'
# Read the form input which is a single line
# guess=25
guess = -1
data = sys.stdin.read()
# print data
try:
    guess = int(data[data.find('=')+1:])
except:
    guess = -1
print 'Your guess is', guess
answer = 42
if guess < answer :
    print 'Your guess is too low'
if guess == answer:
    print 'Congratulations!'
if guess > answer :
    print 'Your guess is too high'

print '</pre>'

print '''<form method="post" action="/">
Enter Guess: <input type="text" name="guess"><br>
<input type="submit">
</form>'''
