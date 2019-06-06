import smbus
import time
import threading

"""
The class serves as the communication between the arduino with i2c,
which the pi is the master
"""
class I2C:
	def __init__(self, slaveAddr):
		self.__RLOCK = threading.RLock()
		self.__I2C_CHANNEL = 1
		self.__COMMUNICATE_INTERVAL = 0.015
		self.__bus = smbus.SMBus(1)
		self.__REG = bytearray(34)
		self.SLAVE_ADDR = slaveAddr

	"""
	Writes data to the slave. Slave address defined in SLAVE_ADDR. User
	is responsible for only write to the register that is meant to do so
	@param reg - The register index to write to. Index defined in Registers class
	@param data - The data to send, the data should only be one byte
	"""
	def write2Slave(self, reg, data):
		self.__RLOCK.acquire()
		time.sleep(self.__COMMUNICATE_INTERVAL)
		try:
			self.__bus.write_byte_data(self.SLAVE_ADDR, reg, data)
		except Exception as e:
			print("i2c write exception ", e)
			self.write2Slave(reg, data)

		self.__RLOCK.release()

	"""
	Write several bytes to target
	@param reg - The target register to write to
	@param data - The data array containing the data sending to reg
	"""
	def writeBytes2Slave(self, reg, data):
		self.__RLOCK.acquire()
		time.sleep(self.__COMMUNICATE_INTERVAL)

		try:
			self.__bus.write_i2c_block_data(self.SLAVE_ADDR, reg, data)
		except Exception as e:
			print("i2c write bytes exception", e)
			self.writeBytes2Slave(reg, data)
		self.__RLOCK.release()

	"""
	Read data from slave. Slave address defined in SLAVE_ADDR. User is responsible
	for only read the register meant to be read.
	@param reg - The register to read data from
	@return A byte size data read from reg
	"""
	def readFromSlave(self, reg):
		self.__RLOCK.acquire()
		time.sleep(self.__COMMUNICATE_INTERVAL)

		output = ""

		try:
			output = self.__bus.read_byte_data(self.SLAVE_ADDR, reg)
		except Exception as e:
			print("i2c read exception", e)
			output = self.readFromSlave(reg)
		self.__RLOCK.release()

		return output

	def read2BytesFromSlave(self, reg):
		self.__RLOCK.acquire()
		time.sleep(self.__COMMUNICATE_INTERVAL)
		output = ""

		try:
			output = self.__bus.read_word_data(self.SLAVE_ADDR, reg)
		except Exception as e:
			print("i2s read 2 bytes exception", e)
			output = self.read4BytesFromSlave(reg)
		self.__RLOCK.release()
	
		return output

	"""
	Reads specified number bytes starting from reg. Can't read more than 32 bytes
	@param reg - The register to read from
	@param val - The mount of bytes to read from, shouldn't be more than 32
	"""
	def readBytesFromSlave(self, reg, val):
		self.__RLOCK.acquire()
		time.sleep(self.__COMMUNICATE_INTERVAL)
		output = 0 
		
		try:
			output = self.__bus.read_i2c_block_data(self.SLAVE_ADDR, reg, val)
		except Exception as e:
			print("i2s read 8 bytes exception", e)
			output = self.readBytesFromSlave(reg, val)
		self.__RLOCK.release()
	
		return output

	"""
	Sets the drive mode to MODE_AUTO or MODE_MANUAL
	@param mode - The mode to set to. Can only be Registers.MODE_AUTO
				  or Registers.MODE_MANUAL
	"""
	def changeDriveMode(self, mode):
		if (mode == Registers.MODE_AUTO 
			or mode == Registers.MODE_MANUAL 
			or mode == Registers.MODE_OFF):
			self.write2Slave(Registers.INDEX_SET_MODE, mode)

	"""
	Get the current drive mode from the arduino
	@return Registers.MODE_AUTO, Registers.MODE_MANUAL or Registers.MODE_OFF
	"""
	def getDriveMode(self):

		return self.readFromSlave(Registers.INDEX_MODE)

	"""
	Sends the data for Joysitck X.
	@param data - The array of data send to the arduino, the size of the data
				  should be 4
	"""
	def setJoyStickX(self, data):
		if len(data) == 4:
			self.writeBytes2Slave(Registers.INDEX_X_HH, data)

	"""
	Sends the data for Joysitck X.
	@param data - The array of data send to the arduino, the size of the data
				  should be 4
	"""
	def setJoyStickY(self, data):
		if len(data) == 4:
			self.writeBytes2Slave(Registers.INDEX_Y_HH, data)

	"""
	@return A array of 4 longs. Each represents the data of the sensor
	"""
	def readSensor1Data(self):
		return self.readBytesFromSlave(Registers.INDEX_SENSOR1_HH, 4)

	"""
	@return A array of 4 longs. Each represents the data of the sensor
	"""
	def readSensor2Data(self):
		return self.readBytesFromSlave(Registers.INDEX_SENSOR2_HH, 4)

	"""
	@return A array of 4 longs. Each represents the data of the sensor
	"""
	def readSensor3Data(self):
		return self.readBytesFromSlave(Registers.INDEX_SENSOR3_HH, 4)

	"""
	@return A array of 4 longs. Each represents the data of the sensor
	"""
	def readSensor4Data(self):
		return self.readBytesFromSlave(Registers.INDEX_SENSOR4_HH, 4)

	"""
	@return A array of 4 longs. Each represents the data of the sensor
	"""
	def readWheel1Data(self):
		return self.readBytesFromSlave(Registers.INDEX_WHEEL1_HH, 4)

	"""
	@return A array of 4 longs. Each represents the data of the sensor
	"""
	def readWheel2Data(self):
		return self.readBytesFromSlave(Registers.INDEX_WHEEL2_HH, 4)

	"""
	Takes a four byte array and turn it into a int
	@param arr - The array that contains four bytes, index 0 is the most
				 significant bytes
	@return an int that was made of the four bytes in the arr
	"""
	def byteArray2Int(self, arr):
		output = 0

		output |= arr[0] << 24
		output |= arr[1] << 16
		output |= arr[2] << 8
		output |= arr[3]

		return output

class Registers:
	# MODE TYPE
	MODE_AUTO = 0x1
	MODE_MANUAL = 0x0
	MODE_OFF = 0x10

	# JOYSTICK X
	INDEX_X_HH = 0x0
	INDEX_X_HL = 0x1
	INDEX_X_LH = 0x2
	INDEX_X_LL = 0x3

	# JOYSTICK Y
	INDEX_Y_HH = 0x4
	INDEX_Y_HL = 0x5
	INDEX_Y_LH = 0x6
	INDEX_Y_LL = 0x7

	# MODES
	INDEX_SET_MODE = 0x8
	INDEX_MODE = 0x9

	# SENSOR 1
	INDEX_SENSOR1_HH = 0xA
	INDEX_SENSOR1_HL = 0xB
	INDEX_SENSOR1_LH = 0xC
	INDEX_SENSOR1_LL = 0xD

	# SENSOR 2
	INDEX_SENSOR2_HH = 0xE
	INDEX_SENSOR2_HL = 0xF
	INDEX_SENSOR2_LH = 0x10
	INDEX_SENSOR2_LL = 0x11

	# SENSOR 3
	INDEX_SENSOR3_HH = 0x12
	INDEX_SENSOR3_HL = 0x13
	INDEX_SENSOR3_LH = 0x14
	INDEX_SENSOR3_LL = 0x15

	# SENSOR 4
	INDEX_SENSOR4_HH = 0x16
	INDEX_SENSOR4_HL = 0x17
	INDEX_SENSOR4_LH = 0x18
	INDEX_SENSOR4_LL = 0x19

	# WHEEL 1
	INDEX_WHEEL1_HH = 0x1A
	INDEX_WHEEL1_HL = 0x1B
	INDEX_WHEEL1_LH = 0x1C
	IDNEX_WHEEL1_LL = 0x1D

	# WHEEL 2
	INDEX_WHEEL2_HH = 0x1E
	INDEX_WHEEL2_HL = 0x1F
	INDEX_WHEEL2_LH = 0x20
	INDEX_WHEEL2_LL = 0x21
