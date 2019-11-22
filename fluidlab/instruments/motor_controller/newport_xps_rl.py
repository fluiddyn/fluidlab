"""

Driver for the Newport Model XPS-RL Motion controller

"""

__all__ = ["NewportXpsRL"]

import socket

NewportXpsRLErrorDescription = {
    2: "Error to ignore",
    1: "TCL interpretor: wrong syntax",
    0: "Successful command",
    -1: "Busy socket: previous command not yet finished",
    -2: "TCP timeout",
    -3: "String command too long",
    -4: "Unknown command",
    -5: "Not allowed due to a positioner error",
    -7: "Wrong format in the command string",
    -8: "Wrong object type for this command",
    -9: "Wrong number of parameters in the command",
    -10: "Wrong parameter type in the command string",
    -11: "Wrong parameters type in the command string: word or word* expected",
    -12: "Wrong parameter type in the command string: bool or bool* expected",
    -13: "Wrong parameter type in the command string: char* expected",
    -14: "Wrong parameter type in the command string: double or double* expected",
    -15: "Wrong parameter type in the command string: int or int* expected",
    -16: "Wrong parameter type in the command string: unsigned int or unsigned int* expected",
    -17: "Parameter out of range",
    -18: "Positioner Name doesn't exist",
    -19: "GroupName doesn't exist or unknown command",
    -20: "Fatal Error during initialization, read the error.log file for more details",
    -21: "Controller in initialization",
    -22: "Not allowed action",
    -23: "Position compare not set",
    -24: "Not available in this configuration",
    -25: "Following Error",
    -26: "Emergency signal",
    -27: "Move Aborted",
    -28: "Home search timeout",
    -29: "Mnemonic gathering type doesn't exist",
    -30: "Gathering not started",
    -31: "Home position is out of user travel limits",
    -32: "Gathering not configurated",
    -33: "Motion done timeout",
    -35: "Not allowed: home preset outside travel limits",
    -36: "Unknown TCL file",
    -37: "TCL Interpretor doesn't run",
    -38: "TCL script can't be killed",
    -39: "Mnemonic action doesn't exist",
    -40: "Mnemonic event doesn't exist",
    -41: "Slave-Master mode not configurated",
    -42: "Jog value out of range",
    -43: "Gathering running",
    -44: "Slave error disabling master",
    -45: "End of run activated",
    -46: "Not allowed action due to backlash",
    -47: "Wrong TCL task name: each TCL task name must be different",
    -48: "BaseVelocity must be null",
    -49: "Inconsistent mechanical zero during home search",
    -50: "Motor initialisation error: check InitializationAcceleration",
    -51: "Spin value out of range",
    -52: "Group interlock",
    -53: "Not allowed action due to a group interlock",
    -60: "Error during file writing or file doesn't exist",
    -61: "Error during file reading or file doesn't exist",
    -62: "Wrong trajectory element type",
    -63: "Wrong XY trajectory element arc radius",
    -64: "Wrong XY trajectory element sweep angle",
    -65: "Trajectory line element discontinuity error or new element is too small",
    -66: "Trajectory doesn't content any element or not loaded",
    -68: "Velocity or trajectory is too high",
    -69: "Acceleration on trajectory is too high",
    -70: "Final velocity on trajectory is not zero",
    -71: "Error write or read from message queue",
    -72: "Error during trajectory initialization",
    -73: "End of file",
    -74: "Error file parameter key not found",
    -75: "Time delta of trajectory element is negative or null",
    -80: "Event not configured",
    -81: "Action not configured",
    -82: "Event buffer is full",
    -83: "Event ID not defined",
    -85: "Secondary positioner index is too far from first positioner",
    -90: "Focus socket not reserved or closed",
    -91: "Focus event scheduler is busy",
    -95: "Error of executing an optional module",
    -96: "Error of stopping an optional module",
    -98: "Error of unloading an optional module",
    -99: "Fatal external module load: see error log",
    -100: "Internal error (memory allocation error, ...)",
    -101: "Relay Feedback Test failed: No oscillation",
    -102: "Relay Feedback Test failed: Signal too noisy",
    -103: "Relay Feedback Test failed: Signal data not enough for analyse",
    -104: "Error of tuning process initialization",
    -105: "Error of scaling calibration initialization",
    -106: "Wrong user name or password",
    -107: "This function requires to be logged in with Administrator rights",
    -108: "The TCP/IP connection was closed by an administrator",
    -109: "Group need to be homed at least once to use this function (distance measured during home search)",
    -110: "Executation not allowed for Gantry configuration",
    -111: "Gathering buffer is full",
    -112: "Error of excitation signal generation initialization",
    -113: "Both ends of run activated",
    -114: "Clamping timeout",
    -115: "Function is not supported by current hardware",
    -116: "Error during external driver initialization, read error.log file for more details",
    -117: "Function is only allowed in DISABLED group state",
    -118: "Not allowed action driver not initialized",
    -119: "Position is outside of travel limits on secondary positioner",
    -120: "Warning following error during move with position compare enabled",
    -121: "Function is not allowed due to configuration disabled",
    -122: "Data incorrect (wrong value, wrong format, wrong order or inexistent)",
    -123: "Action not allowed, an Administrator is already logged in",
    -124: "Error during move of secondary positioner: check positioners errors for details",
    -125: "Check tcl task name is not empty",
    -126: "Wrong parameter type in the command string: short or short* expected",
    -127: "Wrong parameter type in the command string: long or long* expected",
    -128: "Wrong parameter type in the command string: unsigned short or unsigned short* expected",
    -129: "Wrong parameter type in the command string: unsigned long or unsigned long* expected",
    -130: "Wrong parameter type in the command string: float or float* expected",
    -131: "Wrong parameter type in the command string: long long int or long long int* expected",
    -132: "Wrong parameter type in the command string: unsigned long long or unsigned long long* expected",
    -133: "Error when creating actions tasks",
    -134: "Changing the loop status is allowed in DISABLE state only",
    -135: "Function is not allowed because group is not initialized or not referenced",
    -136: "Wrong parameter type in the command string: charhex32* expected",
    -137: "Event&Action: action threads number exceeds limit (must be <= 20)",
    -138: "Event&Action: action thread is running",
    -139: "Event&Action: Always event is not compatible with associated action",
    -200: "Invalid socket",
    -201: "The group is already in this mode",
    -202: "Not allowed action due to an external motion interlock",
    -204: "Function is not allowed because the feed forward is enabled",
    -205: "Not enable in your configuration",
    -206: "Dual encoder position error",
    -207: "Gantry mode error: check Encoder Matrix and Decoupling Motor Matrix",
    -208: "Not allowed action because piston is engaged",
    -209: "INT board command failed: invalid card number or initialization not done",
    -210: "Not allowed action due to (XStart <= Xangle <= XEnd) is not true",
    -211: "Not expected position after motion",
    -212: "MagneticTrackPositionAtHome value is out of tolerance and can not be applied",
    -1000: "Zygo command executation failed",
    -1001: "The controller is connected to Zygo TCP server. Run ZygoStartInterferometer API.",
    -1002: "Connection to Zygo TCP server failed.",
    -1003: "The XPS controller is already connected to Zygo TCP server",
    -1004: "Zygo signal is not present",
    -1005: "Zygo PEG configuration failed",
    -1006: "Zygo error detected",
}


class NewportXpsRLError(Exception):
    """
    Exceptions raised when status is not zero
    """

    def __init__(self, status, response):
        self.status = status
        self.response = response
        status_desc = NewportXpsRLErrorDescription.get(status, "Unknown error")
        self.message = (
            response + ": " + status_desc + " (status: " + str(status) + ")"
        )
        print(self.message)


class NewportXpsRLControllerStatus:
    """
    Controller status flags obtained from ControllerStatusGet()
    See XPS-Unified-ProgrammersManual page 677
    """

    def __init__(self, controller_status):
        self.status = controller_status

    def __str__(self):
        if self.status == 0x00000000:
            return "Controller status OK"
        else:
            status_desc = ""
            if self.status & 0x00000001:
                status_desc += "Controller initialization failed; "
            if self.status & 0x00000002:
                status_desc += "Number of currently opened sockets reached maximum allowed number; "
            if self.status & 0x00000004:
                status_desc += "Controller CPU is overloaded; "
            if self.status & 0x00000008:
                status_desc += "Current measured corrector calculation time exceeds the corrector period; "
            if self.status & 0x00000010:
                status_desc += "Profile generator calculating time exceeds ProfileGeneratorISRRation*IRSCorrectorPeriod; "
            if self.status & 0x00000020:
                status_desc += "Controller has lost a corrector interrupt; "
            if self.status & 0x00000040:
                status_desc += "Zygo interferometer signal is not present; "
            if self.status & 0x00000080:
                status_desc += (
                    "Zygo interferometer Ethernet initialisation failed; "
                )
            if self.status & 0x00000100:
                status_desc += "Zygo interferometer error detected. Please check ZYGO Error Status; "
            if self.status & 0x00000200:
                status_desc += "Motion velocity is limited; "
            if self.status & 0x00000400:
                status_desc += "Lift pin is UP"


class NewportXpsRL:
    def __init__(self, ip_address, port=5001):
        self.ip_address = ip_address
        self.port = port

    def open(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.ip_address, self.port))

    def close(self):
        self.socket.close()

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, type_, value, cb):
        self.close()

    def _parse_chunks(self, chunks):
        data_raw = b"".join(chunks).decode("ascii")
        parsed = data_raw.split(",")
        status = parsed[0]
        eol = parsed[-1]
        if len(parsed) == 3:
            response = parsed[1]
        else:
            response = ",".join(parsed[1:-1])
        if eol != "EndOfAPI":
            print(eol)
            raise RuntimeError("Wrong answer from XPS-RL Controller")
        return int(status), response

    def query(self, command_str):
        if isinstance(command_str, str):
            command_str = command_str.encode("ascii")
        self.socket.sendall(command_str)
        chunks = []
        while True:
            chunk = self.socket.recv(1024)
            if len(chunk) > 0:
                chunks.append(chunk)
            if len(chunks) < 1024:
                break
        return self._parse_chunks(chunks)

    def FirmwareVersionGet(self):
        status, response = self.query("FirmwareVersionGet(char *)")
        if status != 0:
            raise NewportXpsRLError(status, response)
        return response

    def ControllerStatusGet(self):
        status, response = self.query("ControllerStatusGet(int *)")
        if status != 0:
            raise NewportXpsRLError(status, response)
        return NewportXpsRLControllerStatus(int(response))

    def Login(self, username, password):
        status, response = self.query(f"Login({username}, {password}")
        if status != 0:
            raise NewportXpsRLError(status, response)

    def GroupPositionSetpointGet(self, groupname="Group1.Pos"):
        """
        The SetpointPosition is the profiler position. This is the position where the
        positioner should be according to the ideal theoretical motion profile.
        """

        status, response = self.query(
            f"GroupPositionSetpointGet({groupname}, double *)"
        )
        if status != 0:
            raise NewportXpsRLError(status, response)
        return float(response)

    def GroupPositionCurrentGet(self, groupname="Group1.Pos"):
        """
        The CurrentPosition is the encoder position of the stage after mapping corrections are
        applied. This is the actual position of the positioner at this moment of the query.
        """

        status, response = self.query(
            f"GroupPositionCurrentGet({groupname}, double *)"
        )
        if status != 0:
            raise NewportXpsRLError(status, response)
        return float(response)

    def GroupPositionTargetGet(self, groupname="Group1.Pos"):
        """
        The TargetPosition is the final target position commanded by the user.
        """

        status, response = self.query(
            f"GroupPositionTargetGet({groupname}, double *)"
        )
        if status != 0:
            raise NewportXpsRLError(status, response)
        return float(response)

    def GroupMoveAbsolute(self, groupname="Group1.Pos", target=250.0):
        """
        Initiates an absolute move for a positioner or a group.
        """

        status, response = self.query(
            "GroupMoveAbsolute({:}, {:.2f})".format(groupname, float(target))
        )
        if status != 0:
            raise NewportXpsRLError(status, response)


if __name__ == "__main__":

    with NewportXpsRL("192.168.254.254") as xps:
        firmware_version = xps.FirmwareVersionGet()
        controller_status = xps.ControllerStatusGet()

        print("Firmware:", firmware_version)
        print("Status:", controller_status)

        xps.GroupMoveAbsolute(target=0.0)
        pos = xps.GroupPositionTargetGet()
        print("Target position:", pos)

        pos = xps.GroupPositionSetpointGet()
        print("Setpoint position:", pos)
        pos = xps.GroupPositionCurrentGet()
        print("Current position:", pos)
