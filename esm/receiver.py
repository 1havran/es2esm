import SocketServer, random

HOST, PORT = "localhost", 1122
allLogs = "/tmp/all_logs.log"
missedLogs = "/tmp/missed_logs.log"
receivedLogs = "/tmp/received_logs.log"
randomChoice = "abcd"
selfPrint = 1

class MyTCPHandler(SocketServer.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        f_all = open(allLogs, "a+")
        f_missed = open(missedLogs, "a+")
        f_received = open(receivedLogs, "a+")

        self.data = self.request.recv(1024).strip()
        if selfPrint == 1:
            print "{} wrote:".format(self.client_address[0])
            print self.data

        f_all.write(self.data + "\n")
        if random.choice(randomChoice) == "a":
            f_missed.write(self.data + "\n")
        else:
            f_received.write(self.data + "\n")

        f_all.close()
        f_missed.close()
        f_received.close()

        # just send back the same data, but upper-cased
        self.request.sendall(self.data.upper())


if __name__ == "__main__":

    # Create the server, binding to localhost on port 9999
    server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
