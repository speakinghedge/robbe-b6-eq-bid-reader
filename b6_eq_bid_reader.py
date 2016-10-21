"""read and parse messages generated by robbe PowerPeak B6 EQ-BID charger"""
import serial
import json
from time import time


class B6EqBidData(object):
    """holds data parsed/emitted by B6EqBidReader"""
    def __init__(self, v_in, i_in, v_out, i_out, charge):
        self._v_in = v_in
        self._i_in = i_in
        self._v_out = v_out
        self._i_out = i_out
        self._charge = charge
        self._time = time()

    @property
    def v_in(self):
        """return voltage - charger input in milli Volt"""
        return self._v_in

    @property
    def i_in(self):
        """return current - charger input in milli Ampere"""
        return self._i_in

    @property
    def v_out(self):
        """return voltage - charger output in milli Volt"""
        return self._v_out

    @property
    def i_out(self):
        """return current - charger output in milli Ampere"""
        return self._i_out

    @property
    def charge(self):
        """return electric charge - milli Ampere hours"""
        return self._charge

    @property
    def time(self):
        """return timestamp the message was parsed"""
        return self._charge

    def __str__(self):
        return json.dumps(self.__dict__,
                          sort_keys=True, indent=4, separators=(',', ': '))


class B6EqBidReader(object):
    """
    message parser - reads messages from robbe PowerPeak B6 EQ-BID
    via the serial port

    seems the interface is based on a cp210x serial/USB converter using 96008N1

    the message format (as far as I was able to decode):

        \x0c LEN U_IN I_IN U_OUT I_OUT UNKNOWN_FIXED CHK_SUM?
        LEN : ASCII coded, fixed 64 byte message length
        U_IN : hex ASCII coded UINT16 milli Volt
        I_IN : hex ASCII coded UINT16 milli Ampere
        U_OUT : hex ASCII coded UINT16 milli Volt
        I_OUT : hex ASCII coded UINT16 milli Ampere
        P_OUT: hex ASCII coded UINT16 milli Ampere hours
        UNKNOWN_FIXED: 000001000000000000000000000000000
        CHK_SUM: 3 digit hex num, ASCII encoded (not sure about that)

    example:

    \x0c642FA901003DAA00C70009000001000000000000000000000000000ABA\r

    \x0c64
        2FAC - 12204 => 12.204 V
        0100 - 256 => 0.256 A
        3305 - 13061 => 13.061 V
        00C7 - 194 => 0.194 A
        0009 - 9 => 0.009 Ah
        000001000000000000000000000000000A8D\r

    Note: seems there is a bug in the firmware - if the charging process is
    interrupted by an error, i_in turns to 0 and even if the output is disabled
    i_out shows some value

    """
    MESSAGE_PREFIX = '\x0c64'

    def __init__(self, port='/dev/ttyUSB0'):

        self.ser_port = serial.Serial(port=port,
                                      baudrate=9600,
                                      timeout=1,
                                      bytesize=8,
                                      parity=serial.PARITY_NONE,
                                      stopbits=serial.STOPBITS_ONE)

    def read(self):
        """
        read one data set from the serial port and parse contained values

        :return: B6EqBidData object
        """
        retry = 2
        while retry:
            data = self.ser_port.read_until('\r')

            if len(data) == 60:
                if data.startswith(B6EqBidReader.MESSAGE_PREFIX):
                    return B6EqBidData(int(data[3:7], 16),
                                       int(data[7:11], 16),
                                       int(data[11:15], 16),
                                       int(data[15:19], 16),
                                       int(data[19:23], 16))
                else:
                    raise IOError('invalid message format')
            retry -= 1

        raise IOError('failed to read charger message')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.ser_port.close()

if __name__ == '__main__':

    with B6EqBidReader() as reader:

        try:
            while True:
                print reader.read()
        except KeyboardInterrupt:
            pass
