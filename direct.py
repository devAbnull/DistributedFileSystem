import os

directory = raw_input('Enter the filepath:')

if not os.path.exists(directory):
    print "No such directory exists"
else
    print "That directory exists!"
    