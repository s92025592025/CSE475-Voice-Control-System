import sys
import bluetooth
import threading
import concurrent.futures

class Bluetooth:
	RECEIVE_BUFFER = 1024
	def __init__(self, i2c):
		self.__PORT_NUM = 1
		self.__KILL_LOCK = threading.Lock()
		self.__toKill = 0
		self.__i2c = i2c
		self.__createSoc()

	"""
	Create, open, bind, and linsten to socket
	"""
	def __createSoc(self):		
		self.__BT_SOCKET = bluetooth.BluetoothSocket( bluetooth.RFCOMM )
		self.__BT_SOCKET.bind(("", self.__PORT_NUM))
		self.__BT_SOCKET.listen(1)

	"""
	Accects incoming connection in the socket. Sockets needs to be opened, 
	binded, and linstened to before calling this function
	"""
	def __acceptCon(self):
		self.__CLIENT_SOC, self.__BT_ADDR = self.__BT_SOCKET.accept()
		print("Accepted connection from ", self.__BT_ADDR)

	"""
	Receives data from connection
	"""
	def __receive(self):
		return str(self.__CLIENT_SOC.recv(Bluetooth.RECEIVE_BUFFER))

	"""
	Sends data out to client
	"""
	def __send(self, out):
		self.__CLIENT_SOC.send(out.encode())

	"""
	Set the variable saying whether the child theeads should be killed
	@param toKill - 1 for the child to kill, 0 for not to kill
	"""
	def __setKillLock(self, toKill):
		self.__KILL_LOCK.acquire()
		print("in set kill")
		self.__toKill = toKill
		self.__KILL_LOCK.release()
		print("out of setkill")

	def __receiveEvent(self):
		try:
			while True:
				received = self.__receive()
				print("Received: ", received)

				# Send something to i2c
		except Exception as e:
			print("Excpetion in receive event: ", e)
			self.__CLIENT_SOC.close()
			self.__BT_SOCKET.close()
			self.__setKillLock(1)
			sys.exit(0)

	def __sendEvent(self):
		try:
			while True:
				# Get something from i2c
				sensor1Data = self.__i2c.byteArray2Int(self.__i2c.readSensor1Data())
				self.__send("sensor1 " + str(sensor1Data) + "\0")
				sensor2Data = self.__i2c.byteArray2Int(self.__i2c.readSensor2Data())
				self.__send("sensor2 " + str(sensor2Data) + "\0")
				sensor3Data = self.__i2c.byteArray2Int(self.__i2c.readSensor3Data())
				self.__send("sensor3 " + str(sensor3Data) + "\0")
				sensor4Data = self.__i2c.byteArray2Int(self.__i2c.readSensor4Data())
				self.__send("sensor3 " + str(sensor3Data) + "\0")

				wheel1Data = self.__i2c.byteArray2Int(self.__i2c.readWheel1Data())
				self.__send("wheel1 " + str(wheel1Data) + "\0")
				wheel2Data = self.__i2c.byteArray2Int(self.__i2c.readWheel2Data())
				self.__send("wheel2 " + str(wheel2Data) + "\0")

		except Exception as e:
			print("Excpetion in send event: ", e)
			self.__CLIENT_SOC.close()
			self.__BT_SOCKET.close()
			self.__setKillLock(1)
			sys.exit(0)

	"""
	The bluetooth operation
	"""
	def operation(self):
		self.__acceptCon()
		self.__toKill = 0	

		e = concurrent.futures.ThreadPoolExecutor(max_workers=2)
		receiveE = e.submit(self.__receiveEvent)
		sendE = e.submit(self.__sendEvent)
		
		while self.__toKill == 0:
			pass # Hold if everything is fine
		
		print("try reconnect")
		self.__createSoc()
		self.operation()
