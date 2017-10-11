import smbus2 as smbus
from time import sleep
from statistics import median

class Lidar_Lite():
  def __init__(self):
    self.address = 0x62
    self.distWriteReg = 0x00
    self.distWriteVal = 0x04
    self.distReadReg1 = 0x8f
    self.distReadReg2 = 0x10
    self.velWriteReg = 0x04
    self.velWriteVal = 0x08
    self.velReadReg = 0x09

    self.write_wait_time = 0.0025 # 400hz

  def connect(self, bus):
    try:
      self.bus = smbus.SMBus(bus)
      sleep(0.5)
      return 0
    except:
      return -1

  def writeAndWait(self, register, value):
    self.bus.write_byte_data(self.address, register, value);
    sleep(self.write_wait_time)

  def readAndWait(self, register):
    self.bus.write_byte(self.address, register)
    res = self.bus.read_byte(self.address)
    # time.sleep(0.02)
    return res

  def getDistance(self):
    self.writeAndWait(self.distWriteReg, self.distWriteVal)
    dist1 = self.readAndWait(self.distReadReg1)
    dist2 = self.readAndWait(self.distReadReg2)
    return (dist1 << 8) + dist2

  def is_valid(self, d):
    return d > 4 and (d <= 1058 or d > 1200)

  def getSure(self, max_retry = 5, report = False):
    d = self.getDistance()
    count = 0
    while not self.is_valid(d) and count < max_retry:
      count += 1
      d = self.getDistance()

    return d if not report else (d, count)

  def getVelocity(self):
    self.writeAndWait(self.distWriteReg, self.distWriteVal)
    self.writeAndWait(self.velWriteReg, self.velWriteVal)
    vel = self.readAndWait(self.velReadReg)
    return self.signedInt(vel)

  def medianDistance(self, num):
    measurements = []
    for i in range(num):
        measurements.append(self.getDistance())

    return int(round(median(measurements)))


  def signedInt(self, value):
    if value > 127:
      return (256-value) * (-1)
    else:
      return value


