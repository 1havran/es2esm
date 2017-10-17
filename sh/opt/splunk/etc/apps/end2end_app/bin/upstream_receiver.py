import SocketServer, random
import upstream as u
import sys

randomChoice = "abcd"
selfPrint = 1

class MyTCPHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        f_all = open(allLogs, "a+")
        f_missed = open(missedLogs, "a+")
        f_received = open(receivedLogs, "a+")

        self.data = self.request.recv(1024).strip()
        if selfPrint == 1:
            print "{} wrote:".format(self.client_address[0])
            print self.data

        f_all.write(self.data + "\n")
        if random.choice(randomChoice) == randomChoice[0]:
            f_missed.write(self.data + "\n")
        else:
            f_received.write(self.data + "\n")

        f_all.close()
        f_missed.close()
        f_received.close()

        # just send back the same data, but upper-cased
        self.request.sendall(self.data.upper())

def main(argv):
    up = u.Upstream()
    dest = up.getDestinations(-1)
    print "TCP Receiver:",
    if len(argv) < 2:
	receiver = 0
	print "No numeric argument, using argv:1, configuration:" + str(dest)
    else:
        receiver = argv[1]
    i = int(receiver) % len(dest)
    (tag, host, port) = up.getDestinations(i).split(":") 

    allLogs = "/tmp/%s_all_logs.log" % (tag)
    missedLogs = "/tmp/%s_missed_logs.log" % (tag)
    receivedLogs = "/tmp/%s_received_logs.log" % (tag)

    print "TCP Receiver: Listening on %s:%s:%s" % (tag, host, int(port))
    server = SocketServer.TCPServer((host, int(port)), MyTCPHandler)
    server.serve_forever()


if __name__ == "__main__":
    try:
        main(sys.argv)
    except Exception:
        import traceback
        traceback.print_exc(file=sys.stdout)

