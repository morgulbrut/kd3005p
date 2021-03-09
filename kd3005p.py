# -*- coding: utf-8 -*-
#
#  Copyright 2021 morgulbrut, forked from uberdaff
#  Copyright 2017 uberdaff
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#
# Requirement: pyserial, colorama

# getIdn() - Get instrument identification
# setVolt(tal) - Set the voltage on the output
# getVolt() - Get the 'set' voltage
# readVolt() - Get a measurement of the voltage
# setAmp(tal) - Set the current limit
# getAmp() - Get the 'set' current limit
# readAmp() - Get a measurement of the output current
# setOut(bool) - Set the state of the output
# setOcp(bool) - Set the state of the over current protection
# getStatus() - Get the state of the output and CC/CV
#

import sys
import time
import serial
import serial.tools.list_ports
from colorama import Fore, init


class kd3005pInstrument:
    is_connected = False
    psu_com = None
    port_name = "COM1"
    status = {}

    def __init__(self, usb_ids="0416:5011"):
        self.usb_ids = usb_ids
        init(autoreset=True)
        try:
            for p, desc, hwid in sorted(serial.tools.list_ports.comports()):
                # print("{}: {} [{}]".format(p, desc, hwid))
                if hwid.split(" ")[1].split("=")[1] == self.usb_ids:
                    self.port_name = p
            print(self.port_name)
        except IndexError:
            print(Fore.RED + "No powersupply found")
            sys.exit(1)

        try:
            self.psu_com = serial.Serial(
                port=self.port_name,
                baudrate=9600,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS
            )
            self.psu_com.isOpen()
            self.is_connected = True
            self.status = self.getStatus()
        except:
            print(Fore.RED + "COM port failure:")
            print(Fore.RED + str(sys.exc_info()))
            self.psu_com = None
            self.is_connected = False
            sys.exit(1)

    def close(self):
        self.psu_com.close()

    def ser_write_and_recieve(self, data, delay=0.05):  # data er ein stre
        self.psu_com.write(data.encode())
        out = ''
        time.sleep(delay)
        while self.psu_com.inWaiting() > 0:
            out += self.psu_com.read(1).decode()
        if out != '':
            return out
        return None

    def get_Idn(self):
        return self.ser_write_and_recieve("*IDN?", 0.3)

    def set_voltage(self, voltage, delay=0.01):
        self.ser_write_and_recieve("VSET1:"+"{:1.2f}".format(voltage))
        time.sleep(delay)

    def get_voltage(self):
        return self.ser_write_and_recieve("VSET1?")

    def read_voltage(self):
        return self.ser_write_and_recieve("VOUT1?")

    def set_current(self, amp, delay=0.01):
        self.ser_write_and_recieve("ISET1:"+"{:1.3f}".format(amp))
        time.sleep(delay)

    def get_current(self):
        return self.ser_write_and_recieve("ISET1?")

    def read_current(self):
        return self.ser_write_and_recieve("IOUT1?")

    def set_out(self, state):
        if(state == True):
            self.ser_write_and_recieve("OUT1")
        elif(state == False):
            self.ser_write_and_recieve("OUT0")

    def set_opc(self, state):
        if(state == True):
            self.ser_write_and_recieve("OCP1")
        elif(state == False):
            self.ser_write_and_recieve("OCP0")

    def get_status(self):
        stat = ord(self.ser_write_and_recieve("STATUS?")[0])
        if (stat & (1 << 0)) == 0:
            self.status["Mode"] = "CC"
        else:
            self.status["Mode"] = "CV"
        if (stat & (1 << 6)) == 0:
            self.status["Output"] = "Off"
        else:
            self.status["Output"] = "On"
        return self.status
