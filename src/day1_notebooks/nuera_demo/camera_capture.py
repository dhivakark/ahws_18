"""
Camera Capture module. Communicates with C++ Application to receiver captured image
and change sensor related settings
"""

import time
import threading
import app_comm as ac


## Don't Change anything####
_SET = 0x33
_GET = 0x3D

_CMDS = {
   'EXP_AUTO'    :{'sb': 0x01, 't': 'boolean'},
   'EXP_TIME'    :{'sb': 0x02, 't': 'float'},
   'AGAIN_AUTO'  :{'sb': 0x03, 't': 'boolean'},
   'AGAIN'       :{'sb': 0x04, 't': 'float'},
   'START_X'     :{'sb': 0x05, 't': 'integer'},
   'START_Y'     :{'sb': 0x06, 't': 'integer'},
   'WIDTH'       :{'sb': 0x07, 't': 'integer'},
   'HEIGHT'      :{'sb': 0x08, 't': 'integer'},
   'DGAIN_AUTO'  :{'sb': 0x09, 't': 'boolean'},
   'DGAIN_GR'    :{'sb': 0x0A, 't': 'float'},
   'DGAIN_B'     :{'sb': 0x0B, 't': 'float'},
   'DGAIN_R'     :{'sb': 0x0C, 't': 'float'},
   'DGAIN_GB'    :{'sb': 0x0D, 't': 'float'},
   'TRIG_MODE'   :{'sb': 0x0E, 't': 'boolean'}
}
## Don't Change anything####

def cap_loop(ref, timeout=0.5, display_interval=5):
    """
    Capture loops runs in separate thread
    """
    rtry_cnt = 0
    while ref.is_running():
        if not ref.img_socket.check_status():
            rtry_cnt = rtry_cnt + 1
            ref.img_socket.close_connection()
            if ((rtry_cnt + 1) % display_interval) == 0:
                print('Image server trying to reconnect')
                status = ref.img_socket.start_img_rcv(True)
            else:
                status = ref.img_socket.start_img_rcv(False)
            if status:
                rtry_cnt = 0
        time.sleep(timeout)

    return


def check_connection(func):
    """
    Decorator for checking connection
    """
    def check(*args):
        """
        Checks if connected to server. Connects to server
        if not connected.
        """
        instance = args[0]
        if not instance.is_connected():
            instance.connect()
        return func(*args)
    return check


class SensorSetting(object):
    """
    Sensor Settings class. Connects to NUERA_APP
    and updates sensor settings through command server
    """

    def __init__(self, ip='localhost', port_no=7893):
        """
        @param: ip: string. IP Address of camera.
        @param: port_no: int. Port number of command server. Should be
                7893 unless changed in application
        """
        self.__cmd_sock = ac.CmdSocket(ip, port_no)
        self.__ip = ip
        self.__port_no = port_no
        return

    def __del__(self):
        """
        Close connection when reference goes
        """
        self.__cmd_sock.close_connection()
        return

    def connect(self):
        """
        Connect with command server
        """
        return self.__cmd_sock.connect()

    def is_connected(self):
        """
        Check if socket is connect to app
        """
        return self.__cmd_sock.is_connected()

    @check_connection
    def set_x(self, x, last=True):
        """
        Set image sensor starting x coordinate
        @param: x : integer
        @param: last: boolean. set to True if that's last command in bunch update.
                this will help in updating bunch update of setting
        """
        ret = self.__cmd_sock.send_sngl_cmd(_SET, _CMDS['START_X']['sb'], _CMDS['START_X']['t'], x, last)[0]
        return ret

    @check_connection
    def get_x(self):
        """
        Gets current image starting x coordinate
        @return: x: integer x coordiante on success otherwise ''
        """
        ret = self.__cmd_sock.send_sngl_cmd(_GET, _CMDS['START_X']['sb'], _CMDS['START_X']['t'], 0)[1]
        return ret

    @check_connection
    def set_y(self, y, last=True):
        """
        Set image sensor starting y coordinate
        @param: y : integer
        @param: last: boolean. set to True if that's last command in bunch update.
                this will help in updating bunch update of setting
        """
        ret = self.__cmd_sock.send_sngl_cmd(_SET, _CMDS['START_Y']['sb'], _CMDS['START_X']['t'], y, last)[0]
        return ret

    @check_connection
    def get_y(self):
        """
        Gets current image starting y coordinate
        @return: y: integer y coordinate on success otherwise ''
        """
        ret = self.__cmd_sock.send_sngl_cmd(_GET, _CMDS['START_Y']['sb'], _CMDS['START_Y']['t'], 0)[1]
        return ret

    @check_connection
    def set_w(self, w, last=True):
        """
        Set image sensor width
        @param: w : integer
        @param: last: boolean. set to True if that's last command in bunch update.
                this will help in updating bunch update of setting
        """
        ret = self.__cmd_sock.send_sngl_cmd(_SET, _CMDS['WIDTH']['sb'], _CMDS['WIDTH']['t'], w, last)[0]
        return ret

    @check_connection
    def get_w(self):
        """
        Gets current image width
        @return: w: integer
        """
        ret = self.__cmd_sock.send_sngl_cmd(_GET, _CMDS['WIDTH']['sb'], _CMDS['WIDTH']['t'], 0)[1]
        return ret

    @check_connection
    def set_h(self, h, last=True):
        """
        Set image sensor height
        @param: h : integer
        @param: last: boolean. set to True if that's last command in bunch update.
                this will help in updating bunch update of setting
        """
        ret = self.__cmd_sock.send_sngl_cmd(_SET, _CMDS['HEIGHT']['sb'], _CMDS['HEIGHT']['t'], h, last)[0]
        return ret

    @check_connection
    def get_h(self):
        """
        Gets current image height
        @return: h: integer height on success otherwise ''
        """
        ret = self.__cmd_sock.send_sngl_cmd(_GET, _CMDS['HEIGHT']['sb'], _CMDS['HEIGHT']['t'], 0)[1]
        return ret

    @check_connection
    def set_fov(self, x, y, w, h, last=True):
        """
        Sets FOV of image sensor
        @param: x: starting x coordinat, y: starting y coordinate, w: width
                h: height
        @param: last: boolean. set to True if that's last command in bunch update.
                this will help in updating bunch update of setting
        @return: True on success otherwise False
        """
        ret = False
        ret |= self.set_x(x, False)[0]
        ret |= self.set_y(y, False)[0]
        ret |= self.set_w(w, False)[0]
        ret |= self.set_h(h, last)[0]

        return ret

    @check_connection
    def get_fov(self):
        """
        Returns the current field of view of
        image sensor
        @return: tuple(x, y, w, h)
        """
        ret = False
        x = self.get_x()[1]
        y = self.get_y()[1]
        w = self.get_w()[1]
        h = self.get_h()[1]

        return (x, y, w, h)

    @check_connection
    def set_auto_analog_gain(self, is_auto, last=True):
        """
        Set image sensor to auto analog gain mode.
        If auto mode is abled, use set_analog_gain function
        to control gain values
        @param: is_auto: boolean. true for auto mode
        """
        ret = self.__cmd_sock.send_sngl_cmd(_SET, _CMDS['AGAIN_AUTO']['sb'], _CMDS['AGAIN_AUTO']['t'], is_auto, last)[0]
        return

    @check_connection
    def get_auto_analog_gain(self):
        """
        Get camera exposure mode
        @return: True on auto mode otherwise false
        for manual mode
        @param: last: boolean. set to True if that's last command in bunch update.
                this will help in updating bunch update of setting
        """
        ret, is_auto = self.__cmd_sock.send_sngl_cmd(_GET, _CMDS['AGAIN_AUTO']['sb'], _CMDS['AGAIN_AUTO']['t'], False)
        return bool(is_auto)

    @check_connection
    def set_analog_gain(self, gain, last):
        """
        Sets analog gain for pixel
        @param: gain: Float.
        @param: last: boolean. set to True if that's last command in bunch update.
                this will help in updating bunch update of setting
        """
        ret = self.__cmd_sock.send_sngl_cmd(_SET, _CMDS['AGAIN']['sb'], _CMDS['AGAIN']['t'], gain, last)[0]
        return ret

    @check_connection
    def get_analog_gain(self):
        """
        Gets the current analog gain
        @return: float. gain value
        @param: last: boolean. set to True if that's last command in bunch update.
                this will help in updating bunch update of setting
        """
        ret, gain = self.__cmd_sock.send_sngl_cmd(_GET, _CMDS['AGAIN']['sb'], _CMDS['AGAIN']['t'], 0.0)
        return gain

    @check_connection
    def set_auto_digital_gain(self, is_auto, last=True):
        """
        Set image sensor to auto digial gain mode.
        If auto mode is enabled, use set_digital_gain function
        to control gain values
        @param: is_auto: boolean. true for auto mode
        @param: last: boolean. set to True if that's last command in bunch update.
                this will help in updating bunch update of setting
        """
        ret = self.__cmd_sock.send_sngl_cmd(_SET, _CMDS['DGAIN_AUTO']['sb'], _CMDS['DGAIN_AUTO']['t'], is_auto, last)[0]
        return ret

    @check_connection
    def get_auto_digital_gain(self):
        """
        Get camera exposure mode
        @return: True on auto mode otherwise false
         for manual mode
        """
        ret, is_auto = self.__cmd_sock.send_sngl_cmd(_GET, _CMDS['DGAIN_AUTO']['sb'], _CMDS['DGAIN_AUTO']['t'], 0)
        return bool(is_auto)

    @check_connection
    def set_dgain_gr(self, gr, last=True):
        """
        Digital Gain for Green Channel in Red rows
        @param: gb: Gain to be set. Refer: datasheet for more info
        @param: last: boolean. set to True if that's last command in bunch update.
                this will help in updating bunch update of setting
        """
        ret = self.__cmd_sock.send_sngl_cmd(_SET, _CMDS['DGAIN_GR']['sb'], _CMDS['DGAIN_GR']['t'], gr, last)[0]
        return

    @check_connection
    def get_dgain_gr(self):
        """
        Digital Gain for Green Channel in Red rows
        @return: float value
        """
        gr = self.__cmd_sock.send_sngl_cmd(_GET, _CMDS['DGAIN_GR']['sb'], _CMDS['DGAIN_GR']['t'], 0.0)[1]
        return gr

    @check_connection
    def set_dgain_gb(self, gb, last=True):
        """
        Digital Gain for Green Channel in Blue rows
        @param: gb: Gain to be set.Refer: datasheet for more info
        @param: last: boolean. set to True if that's last command in bunch update.
                this will help in updating bunch update of setting
        """
        ret |= self.__cmd_sock.send_sngl_cmd(_SET, _CMDS['DGAIN_GB']['sb'], _CMDS['DGAIN_GB']['t'], gbi, last)[0]
        return

    @check_connection
    def get_dgain_gb(self):
        """
        Digital Gain for Green Channel in Blue rows
        @return: float value
        """
        gb = self.__cmd_sock.send_sngl_cmd(_GET, _CMDS['DGAIN_GB']['sb'], _CMDS['DGAIN_GB']['t'], 0.0)[1]
        return gb

    @check_connection
    def set_dgain_r(self, r, last=True):
        """
        Digital Gain for Red Channel
        @param: r: Red gain to be set.Refer: datasheet for more info
        @param: last: boolean. set to True if that's last command in bunch update.
                this will help in updating bunch update of setting
        """
        ret = self.__cmd_sock.send_sngl_cmd(_SET, _CMDS['DGAIN_R']['sb'], _CMDS['DGAIN_R']['t'], r, last)[0]
        return ret

    @check_connection
    def get_dgain_r(self):
        """
        Digital Gain for Red Channel
        @return: float value
        """
        r = self.__cmd_sock.send_sngl_cmd(_GET, _CMDS['DGAIN_R']['sb'], _CMDS['DGAIN_R']['t'], 0.0)[1]
        return r


    @check_connection
    def set_dgain_b(self, b, last=True):
        """
        Digital Gain for Blue Channel
        @param: b: blue gain to be set.Refer: datasheet for more info
        @param: last: boolean. set to True if that's last command in bunch update.
                this will help in updating bunch update of setting
        """
        ret = self.__cmd_sock.send_sngl_cmd(_SET, _CMDS['DGAIN_B']['sb'], _CMDS['DGAIN_B']['t'], b, last)[0]
        return ret

    @check_connection
    def get_dgain_b(self):
        """
        Digital Gain for Blue Channel
        @return: float value
        """
        b = self.__cmd_sock.send_sngl_cmd(_GET, _CMDS['DGAIN_B']['sb'], _CMDS['DGAIN_B']['t'], 0.0)[1]
        return b

    @check_connection
    def set_digital_gain(self, gr, gb, r, b, last=True):
        """
        Sets digital gain for individual colors in
        bayer filter
        @param: gr: float, green gain in red rows
        @param: gb: float, green gain in blue rows
        @param: r: red gain
        @param: b: blue gain
        @param: last: boolean. set to True if that's last command in bunch update.
                this will help in updating bunch update of setting
        """
        ret = False
        ret = self.set_dgain_gr(gr)
        ret = self.set_dgain_gb(gb)
        ret = self.set_dgain_r(r)
        ret = self.set_dgain_b(b, last)

        return ret

    @check_connection
    def get_digital_gain(self):
        """
        Gets the current digital gain for individual
        colors in bayer filter
        @return: tuple(gr, gb, r, b)
        """
        gr = get_dgain_gr()
        gb = get_dgain_gb()
        r = get_dgain_r()
        b = get_dgain_b()

        return gr, gb, r, b

    @check_connection
    def set_capture_mode(self, is_trigger, last=True):
        """
        Set camera capture mode.
        @param: is_trigger: boolean. True for trigger mode otherwise
        continuous mode
        @param: last: boolean. set to True if that's last command in bunch update.
                this will help in updating bunch update of setting
        """
        ret = self.__cmd_sock.send_sngl_cmd(_SET, _CMDS['TRIG_MODE']['sb'], _CMDS['TRIG_MODE']['t'], is_trigger, True)[0]
        return ret

    @check_connection
    def get_capture_mode(self):
        """
        Get camera capture mode.
        @return: True on trigger mode otherwise false for continuous mode
        """
        ret, is_trigger = self.__cmd_sock.send_sngl_cmd(_GET, _CMDS['TRIG_MODE']['sb'], _CMDS['TRIG_MODE']['t'], False)
        return bool(is_trigger)

    @check_connection
    def set_auto_exposure(self, is_auto, last=True):
        """
        Set image sensor to auto exposure mode.
        @param: is_auto: boolean. true for auto mode
        @param: last: boolean. set to True if that's last command in bunch update.
                this will help in updating bunch update of setting
        """
        ret = self.__cmd_sock.send_sngl_cmd(_SET, _CMDS['EXP_AUTO']['sb'], _CMDS['EXP_AUTO']['t'], is_auto, last)[0]
        return ret

    @check_connection
    def get_auto_exposure(self):
        """
        Get camera exposure mode
        @return: True on auto mode otherwise false for manual mode
        @param: last: boolean. set to True if that's last command in bunch update.
                this will help in updating bunch update of setting
        """
        ret, is_auto = self.__cmd_sock.send_sngl_cmd(_GET, _CMDS['EXP_AUTO']['sb'], _CMDS['EXP_AUTO']['t'], False)
        return bool(is_auto)

    @check_connection
    def set_exposure_time(self, exp_time, last=True):
        """
        Sets exposure time for image sensor. Works only when auto exposture is disabled
        @param: float. exposure time
        @param: last: boolean. set to True if that's last command in bunch update.
                this will help in updating bunch update of setting
        """
        ret = self.__cmd_sock.send_sngl_cmd(_SET, _CMDS['EXP_TIME']['sb'], _CMDS['EXP_TIME']['t'], exp_time, last)[0]
        return ret

    @check_connection
    def get_exposure_time(self):
        """
        TODO: Need to make in us or ms
        Gets exposure time of image sensor
        @return: float. exposure time on success otherwise ''
        """
        ret, time = self.__cmd_sock.send_sngl_cmd(_GET, _CMDS['EXP_TIME']['sb'], _CMDS['EXP_TIME']['t'], 0.0)
        return time


class CameraStreamer(SensorSetting):

  def __init__(self, callback, server="0.0.0.0", port_no=7891):
      """
      @param: callback: Function which will be called whenever a frame arrives
      @param: server:string. IP address of camera to connect to
      @param: port_no: integer. Image server port number. 7891 unless
              updated in the application
      """
      self.__server = server
      self.__port_no = port_no
      self.img_socket = ac.ImageSocket(self.__server, self.__port_no)
      self.img_socket.register_img_cb(callback)
      super(CameraStreamer, self).__init__(server, 7893) # command server port no
      self.__is_running = False
      return

  def start_capture(self, timeout=0.5, display_interval=5):
      """
      Handles any connection failure in between. Runs in infinite loop
      @params: timeout in s for loop time
      @return: None
      """
      self.__thread = threading.Thread(target=cap_loop, args=(self, timeout, display_interval))
      self.__thread.daemon = True
      self.img_socket.start_img_rcv(True)
      self.__is_running = True
      self.__thread.start()
      return

  def is_running(self):
      """
      Returns status of image capturing loop
      @return: True if running otherwise False
      """
      return self.__is_running

  def stop_capture(self):
      """
      Stops application & cleans
      """
      self.__is_running = False
      self.img_socket.stop_img_rcv()
      while self.img_socket.check_status():
        print('Trying to stop')
        time.sleep(0.25)  # Loop untill thread closes safely
      return True
