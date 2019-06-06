import sys
import re
import bluetooth
import threading
import concurrent.futures

class Bluetooth:
	RECEIVE_BUFFER = 1024
	SEND_PACKET_END_MARKER = '\0'
	RECV_PACKET_END_MARKER = '\0'
	JOYSTICK_X_REG = re.compile("X [0-9]+")
	JOYSTICK_Y_REG = re.compile("Y [0-9]+")
	SETMODE_REG = re.compile("SETMODE [0-9]+")

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
		return self.__CLIENT_SOC.recv(Bluetooth.RECEIVE_BUFFER).decode('utf-8')

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
		self.__toKill = toKill
		self.__KILL_LOCK.release()

	def __receiveEvent(self):
		receiveBuffer = ""
		try:
			while True:
				receiveBuffer += self.__receive()
				print("Received Buffer: ", receiveBuffer)

				# Send something to i2c
				receiveBuffer = self.__processRecvBuffer(receiveBuffer)
				print("Remaining Buffer: ", receiveBuffer)
		except Exception as e:
			print("Excpetion in receive event: ", e)
			self.__CLIENT_SOC.close()
			self.__BT_SOCKET.close()
			self.__setKillLock(1)
			sys.exit(0)

	"""
	Takes the buffer received from client, process the commands a much as possible.
	@param recvBuf - The buffer that the host received
	@return The rest of the buffer that we can't process
	"""
	def __processRecvBuffer(self, recvBuf):
		packets = recvBuf.split(Bluetooth.RECV_PACKET_END_MARKER)
		recvBuf = ""
		
		for packet in packets:
			packet = packet.strip()
			print("packet: ", packet)

			if Bluetooth.JOYSTICK_X_REG.fullmatch(packet):
				arr = packet.split(" ")
				print("arr[1]: ", int(arr[1]))
				data = int(arr[1])#.to_bytes(4, byteorder = 'big')
				output = [(data >> 24) & 0xFF, (data >> 16) & 0xFF, (data >> 8) & 0xFF,
						(data) & 0xFF]
				print(data)
				print("output: ", output)
				self.__i2c.setJoyStickX(output)
			elif Bluetooth.JOYSTICK_Y_REG.fullmatch(packet):
				arr = packet.split(" ")
				data = int(arr[1]).to_bytes(4, byteorder = 'big')
				#self.__i2c.setJoyStickY(data)
			elif Bluetooth.SETMODE_REG.fullmatch(packet):
				arr = packet.split(" ")
				self.__i2c.changeDriveMode(int(arr[1]))
			else:
				recvBuf += packet

		return recvBuf

	def __bytesArray2IntArray(self, data):
		output = []

		for i in range(4):
			output[i] = int.from_bytes(data[i], 'big')

		return output

	def __sendEvent(self):
		try:
			while True:
				# Get something from i2c
				sensor1Data = self.__i2c.byteArray2Int(self.__i2c.readSensor1Data())
				self.__send("sensor1 " + str(sensor1Data) + Bluetooth.SEND_PACKET_END_MARKER)
				sensor2Data = self.__i2c.byteArray2Int(self.__i2c.readSensor2Data())
				self.__send("sensor2 " + str(sensor2Data) + Bluetooth.SEND_PACKET_END_MARKER)
				sensor3Data = self.__i2c.byteArray2Int(self.__i2c.readSensor3Data())
				self.__send("sensor3 " + str(sensor3Data) + Bluetooth.SEND_PACKET_END_MARKER)
				sensor4Data = self.__i2c.byteArray2Int(self.__i2c.readSensor4Data())
				self.__send("sensor3 " + str(sensor3Data) + Bluetooth.SEND_PACKET_END_MARKER)

				wheel1Data = self.__i2c.byteArray2Int(self.__i2c.readWheel1Data())
				self.__send("wheel1 " + str(wheel1Data) + Bluetooth.SEND_PACKET_END_MARKER)
				wheel2Data = self.__i2c.byteArray2Int(self.__i2c.readWheel2Data())
				self.__send("wheel2 " + str(wheel2Data) + Bluetooth.SEND_PACKET_END_MARKER)

				modeData = self.__i2c.getDriveMode()
				self.__send("MODE " + str(modeData) + Bluetooth.SEND_PACKET_END_MARKER)

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
