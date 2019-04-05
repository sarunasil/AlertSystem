pipe = "/tmp/communication"
pipefile = open(pipe, 'r')

while True:
    line = pipefile.readline()
    print(line)
