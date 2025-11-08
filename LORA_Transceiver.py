# LORA_Transceiver 
# based on online code, adapted for DXLR02
# AT Commands for this device use a comma instead of =
# frequency 433 is incorrect for Australia, and should be 915 (I purchased the wrong module!)
# 2 Nov 2025
# updated 7 Nov 2025


from machine import UART, Pin
from utime import sleep_ms
import select

DELAY = 100 # ms

class LORA_Transceiver():
    
    def __init__(self, radio_frequency = 433, channel = 0, power = 12, poll_timeout = 1): # timeout in seconds
        self.estatus = False
        self.last_error = ''
        self.name = 'LORA transceiver ' + str(radio_frequency) + ' MHz'
        self.rfreq = radio_frequency
        self.channel = channel
        self.power = power
        self.timeout = poll_timeout * 1000
        self.uart = UART(1, baudrate=9600,  tx=Pin(4), rx=Pin(5), timeout=1000) # same pins used for Pico and Pico Zero
        self.poll = select.poll()
        self.poll.register(self.uart, select.POLLIN)
        sleep_ms(1000)
        return
    
    def activate(self):  
        status = self.send_AT('+++') # enter AT mode
        if 'Entry AT' in status:
            status = self.send_AT('AT')
        else:
            self.estatus = True
            self.last_error = 'LORA init error'
        if 'OK' in status: # if the previous AT command works, the remaining AT commands should also work (note they return messages and not 'OK')
            status = self.send_AT('AT+BAUD,4') # 4 = 9600
            status = self.send_AT('AT+SF,7')
            status = self.send_AT('AT+MODE,0')
            status = self.send_AT('AT+POWE,' + str(self.power)) # 22 max
            status = self.send_AT('AT+CHANNEL,' + str(self.channel)) # for P2P, the same channel must be used
            status = self.send_AT('+++') # exit AT mode
        else:
            self.estatus = True
            self.last_error = 'LORA activation error'
        return

    def send_AT(self, command):
        response= self.send_data(command + '\r\n')
        return response

    def send_data(self, data_str):
        buffer = data_str # + '\r\n'
        nc = self.uart.write(buffer)
        sleep_ms(DELAY)
        response = self.get_response()
        return response
        
    def get_response(self): 
        presult = self.poll.poll(self.timeout)
        response = ''
        try:
            rdata = self.uart.readline() # allow for multiline responses (e.g. HELP)
            while rdata:
                response += rdata.decode('utf-8')
                rdata = self.uart.readline()
                if rdata:
                    response += '\n' # more data, add a newline
        except UnicodeError as e:
            response += '\nUnicode invalid' # sometimes occurs, can be ignored
        return response
        
    def get_message(self): 
        data_str = self.get_response()
        dtuple = data_str.split(',') # including a tuple to match RF method of the same name
        return (data_str, dtuple)

    def send_message(self, data_str):
        response = self.send_data(data_str)
        return response
    
    def get_name(self):
        return self.name

    def get_frequency(self):
        return self.rfreq # MHz   #can't see how to determine the actual frequency - use constant for now
    
    def get_channel(self):
        return self.channel
    
    def get_power(self):
        return self.power
    
    def get_baud(self):
        return 9600

    def check_error(self):
        return self.estatus
    
    def get_error(self):
        return self.last_error




