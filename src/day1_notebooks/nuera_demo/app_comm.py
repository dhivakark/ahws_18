"""
Communication between Camera and Python Server
Connection to Data Server @port:7892 and Command Server @port:7891
"""

import time
import struct
import socket
import threading


_CMD_TYPE = {
        'boolean': ('b', bool),
        'string': ('s', str),
        'integer': ('i', int),
        'float': ('f', float),
        'double': ('d', float),
        'dropdown': ('i', int),
        'radio': ('i', int),
        'button': ('b', bool)
}


def get_vl_fmt(dtype, value):
    """
    Maps datatype for pack function
    """
    if dtype not in _CMD_TYPE:
        dtype = 'string'

    if dtype == 'string':
        vl_fmt = str(len(value) + 1) + _CMD_TYPE[dtype][0]
    else:
        vl_fmt = _CMD_TYPE[dtype][0]

    return vl_fmt


def map_to_py_dtype(dtype, value):
    """
    Maps datatype into Python dtypes
    """
    if dtype in _CMD_TYPE:
        if dtype == 'boolean':
          py_value = bool(int(value))
        else:
          py_value = _CMD_TYPE[dtype][1](value)
    else: # other dtypes are string by default
        py_value = value

    return py_value


def recv_loop(ref):
    """
    Continous receives image and calls callback function present in
    ref. Stops when recv fails (server is closed or socket is closed)
    Called after socket has been created & connected to Camera
    @param: ref: ImageSocket class instance
    @return True
    """
    fmt = '=B H H I B'
    hdr_size = struct.calcsize(fmt)
    while not ref.event.is_set():
        #TODO: Add socket receive
        try:
            img_hdr = ref.socket.recv(hdr_size, 0)
        except:
            print ('Connection reset')
            break

        if len(img_hdr) != hdr_size:
            print ('recv failed with error: {}'.format(str(img_hdr)))
            break

        hdr, w, h, sz, ftr = struct.unpack(fmt, img_hdr) # "=" is added remove padding
        if hdr == 0xAA and ftr == 0x55:
            img_data = bytearray([])
            tmp = ref.socket.recv(sz, 0)
            if len(tmp) <= 0: break;
            img_data.extend(bytearray(tmp))
            lngth = len(tmp)
            while lngth < sz:
                rem = sz - lngth
                tmp = ref.socket.recv(rem, 0)
                if len(tmp) <= 0: break;    # Inner loop closes first & then external loop after next read call
                lngth = lngth + len(tmp)
                img_data.extend(bytearray(tmp))
            if ref._cb is not None:
                ref._cb({'img': img_data, 'h': h, 'w': w})
    print ('IMG CLIENT: Disconnected')
    return


class ImageSocket(object):
    """
    Image socket has to be connected and stream images continuously and
    disconnect Handle accordingly
    """

    def __init__(self, ip="localhost", port=7891):
        """
        @param: ip:string. IP address of camera to connect to
        @param: port_no: integer. Image server port number. 7891 unless
                updated in the application
        """
        self.__ip, self.__port = ip, port
        self.event, self.thread = None, None
        self._cb, self.__thrd_strtd = None, False
        return

    def register_img_cb(self, func):
        """
        Register callback function for image receiving loop
        @params: func: function  pointer prototype is def callback({'img':
        <jpeg_img>, 'w': width, 'h': height })
        """
        self._cb = func
        return

    def start_img_rcv(self, debug=False):
        """
        Connect to Image server & get images
        @params: None
        @return: True on success otherwise False
        """
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.__ip, self.__port))
        except:
            if debug:
              print ("Image Server Connection Failed\n")
            return False
        self.event = threading.Event()
        self.thread = threading.Thread(target=recv_loop, name="Img Recv Thread", args=(self, ))
        self.thread.deamon = True  #needed to kill this thread when python is killed
        self.thread.start()
        self.__thrd_strtd = True
        print ('IMG CLIENT: Connected')
        return True

    def check_status(self):
        """
        Check if image receiving thread is ON
        @returns: True on running otherwise False
        """

        return self.thread.is_alive() if self.__thrd_strtd else False

    def stop_img_rcv(self):
        """
        Stops image receiving loop by setting event which is running
        in separate thread. Waits indefinitely till thread joins
        @param: None
        @return: None
        """
        if self.__thrd_strtd:
            self.event.set()
            time.sleep(0.25)
            print ('Waiting to join')
            self.thread.join()
            self.__thrd_strtd = False
        return

    def close_connection(self):
        """
        Closes connection with server
        @params: None
        @returns: None
        """
        if self.__thrd_strtd:
            if self.socket is not None:
                try:
                    self.socket.shutdown(socket.SHUT_RDWR)
                    self.socket.close()
                except:
                    print ('Server is dead without informing')
                self.socket = None
                self.__thrd_strtd = False
        return


class CmdSocket(object):
    """
    Command Socket has to be connected & disconnected for each & every command
    Handle accordingly
    """

    def __init__(self, ip="localhost", port=7893):
        """
        @param: ip:string. IP address of camera to connect to
        @param: port_no: integer. Image server port number. 7893 unless
                updated in the application
        """
        self.__socket = None
        self.__port = port
        self.__ip = ip
        self.__is_connected = False
        return

    def connect(self):
        """
        Make connection to server
        """
        try:
            self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.__socket.connect((self.__ip, self.__port))
        except:
            self.__socket = None
            print ('Command: Connection failed')
            return False
        print ('CMD CLIENT: Connected')
        self.__is_connected = True
        return True

    def is_connected(self):
        """
        Check if socket is connected
        """
        return self.__is_connected


    def send_sngl_cmd(self, cmd, subcmd, cmd_type, value, is_last_cmd=False):
        """
        Send Command to App & read response
        """
        vl_fmt = get_vl_fmt(cmd_type, value)
        value = map_to_py_dtype(cmd_type, value)
        vl_data = struct.pack('=' + vl_fmt, value)
        # Command format : (cmd, subcmd, error, param_size, parameter_value)
        cmd_data = struct.pack('=IIII', int(cmd), int(subcmd), 0, len(vl_data))
        snd_cmd = cmd_data + vl_data
        if(len(vl_data) % 2 != 0):
            snd_cmd += struct.pack('=b', False)
        rcvd = ''
        #TODO: Handle incomplete data transfer
        try:
            snt_cmd = self.__socket.send(snd_cmd, len(snd_cmd))
            rcv = self.__socket.recv(16)
            is_success = (snt_cmd == len(snd_cmd)) and (16 == (len(rcv)))
            (_, _, _, size) = struct.unpack("=IIII", rcv)
            if is_last_cmd and size == 0: # size ==0 for get commands
                print("UPDATE COMMAND")
                # Last command to update setting in camera
                cmd_data = struct.pack('=IIII', 50, 0, 0, 0)
                snt_len = self.__socket.send(cmd_data, len(cmd_data))
                rcv = self.__socket.recv(16)
                is_success = (snt_len == len(cmd_data)) and (len(rcv) == 16)
            else:
                rcv = self.__socket.recv(size)
                rcvd = struct.unpack('=' + vl_fmt, rcv)[0]
        except:
            is_success = False

        if not is_success: self.close_connection()

        return is_success, rcvd

    def close_connection(self):
        """
        Shutdown socket & close it
        """
        if self.__socket is not None:
            print ('CMD CLIENT: Disconnected')
            try:
               self.__socket.shutdown(socket.SHUT_RDWR)
               self.__socket.close()
            except:
                print ('Server closed without informing')
        self.__is_connected = False
        return
