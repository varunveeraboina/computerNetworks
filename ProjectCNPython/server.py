from socket import *
import pickle as pkl
import sys
import hashlib

serverSocket = socket(AF_INET, SOCK_DGRAM)	
serverSocket.bind(('127.0.0.1', 12345))

print("SERVER IS READY.")

track =[]
output = bytearray()
pkt =[]
rcvd = False
seqCheck = 1


while True:
	try:
		block, address = serverSocket.recvfrom(4096)
		pkt = pkl.loads(block)
		checksumReceived = pkt[-1]
		del pkt[-1]
		checksumCalculated = hashlib.sha1()
		checksumCalculated.update(pkl.dumps(pkt))
		checksumCalculated=checksumCalculated.digest()
		rcvd = True
	except :
		rcvd = False

	if (rcvd == True and pkt[0] == seqCheck and checksumCalculated == checksumReceived ) :
		seqCheck += 1
		pkt = pkl.loads(block)
		print ("Recieved" + str(pkt[0]))

		if pkt[0] in track:
			ACK = []
			ACK.append(pkt[0])
			ACK.append("ACK")
			checksum = hashlib.sha1()
			checksum.update(pkl.dumps(ACK))
			ACK.append(checksum.digest())
			SACK = pkl.dumps(ACK)
			serverSocket.sendto(SACK, (address[0], address[1]))
			print ("Sent ACK" + str(ACK[0]))

		else :
			track.append(pkt[0])
			data = pkt[1]
			ACK = []
			ACK.append(pkt[0])
			ACK.append("ACK")
			checksum = hashlib.sha1()
			checksum.update(pkl.dumps(ACK))
			ACK.append(checksum.digest())
			SACK = pkl.dumps(ACK)
			serverSocket.sendto(SACK, (address[0], address[1]))	
			if data=="EOF":							
				break							
			output=output+data						
			rcvd = False
			print ("Sent ack" +  str(ACK[0]))
	else :
		ACK = []
		ACK.append("ACK")
		checksum = hashlib.sha1()
		checksum.update(pkl.dumps(ACK))
		ACK.append(checksum.digest())
		SACK = pkl.dumps(ACK)
		serverSocket.sendto(SACK, (address[0], address[1]))	

file = open("recvd.txt", "wb")
file.write(output)
file.close

print("File Received. Closing Socket.")
serverSocket.close()
