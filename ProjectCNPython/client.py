from socket import *
import datetime
import hashlib
import sys
import pickle as pkl
import os


blockSize = 500
seqNo = 1
pktList = [] #Empty List to store packets
timeout = 0.1
ack = False
seqCheck = 1
DACK = []


fileName = input("Enter Filename:")
file = open(fileName, "rb")
fileSize = os.stat(fileName).st_size
block = file.read(blockSize)
while block:
	pkt =[]
	pkt.append(seqNo)
	pkt.append(block)
	pktList.append(pkt)
	seqNo += 1
	block = file.read(blockSize)
pktList.append([seqNo, "EOF"])
seqNo +=1
file.close()

packetNo = len(pktList)

clientSocket=socket(AF_INET,SOCK_DGRAM) 
clientSocket.settimeout(timeout)	
startTime = datetime.datetime.now()

while pktList:
	pktSend = pktList[0]
	checksum = hashlib.sha1()
	checksum.update(pkl.dumps(pktSend))
	pktSend.append(checksum.digest())
	pktSerialized = pkl.dumps(pktSend)
	clientSocket.sendto(pktSerialized, ("127.0.0.1", 12345))
	try: 
		ACK, address = clientSocket.recvfrom(4096)
		DACK = pkl.loads(ACK)
		checksumReceived = DACK[-1]
		del DACK[-1]
		checksumCalculated = hashlib.sha1()
		checksumCalculated.update(pkl.dumps(DACK))
		checksumCalculated = checksumCalculated.digest()
		ack = True
	except:
		ack = False
		print("\nTimeout.")

	if(ack == True and DACK[0] == seqCheck and checksumCalculated == checksumReceived):
		seqCheck += 1
		del pktList[0]

	else:
		continue

print("Time taken: " + str((datetime.datetime.now() - startTime).total_seconds()))
print("Number of packets: " + str(packetNo))
print("File size: " + str(fileSize) + "bytes")
print("\nFile sent successfully. Closing connection.")
clientSocket.close()

