"""CozyLife device control class."""
import socket
import json
import time
import logging
from .const import CMD_SET, CMD_QUERY, CMD_INFO

_LOGGER = logging.getLogger(__name__)

class CozyLifeDevice:
    """Class to communicate with CozyLife devices."""

    def __init__(self, ip, port=5555):
        """Initialize the device."""
        self.ip = ip
        self.port = port
        self._socket = None
        self._connect_timeout = 3
        self._read_timeout = 2
        self._last_connect_attempt = 0
        self._connect_retry_delay = 30  # Seconds between connection attempts

    def test_connection(self):
        """Test if we can connect to the device."""
        try:
            self._ensure_connection()
            # Try to query device state
            result = self.query_state()
            return result is not None
        except Exception:
            return False
        finally:
            self._close_connection()

    def _ensure_connection(self):
        """Ensure connection is established."""
        current_time = time.time()
        
        # If connection exists, return True
        if self._socket is not None:
            return True
            
        # Check if we should retry connection
        if (current_time - self._last_connect_attempt) < self._connect_retry_delay:
            return False

        self._last_connect_attempt = current_time
        
        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.settimeout(self._connect_timeout)
            self._socket.connect((self.ip, self.port))
            return True
        except Exception as e:
            _LOGGER.debug(f"Connection failed to {self.ip}: {e}")
            self._close_connection()
            return False

    def _close_connection(self):
        """Close the connection safely."""
        if self._socket:
            try:
                self._socket.close()
            except Exception:
                pass
            finally:
                self._socket = None

    def _get_sn(self):
        """Generate sequence number."""
        return str(int(round(time.time() * 1000)))

    def _read_response(self):
        """Read response from socket with proper handling of multiple JSON objects."""
        if not self._socket:
            return None

        try:
            self._socket.settimeout(self._read_timeout)
            data = ""
            while True:
                chunk = self._socket.recv(1024).decode('utf-8')
                if not chunk:
                    break
                data += chunk
                if '\n' in data:
                    # Take only the first complete JSON object
                    json_data = data.split('\n')[0]
                    try:
                        return json.loads(json_data)
                    except json.JSONDecodeError:
                        continue
        except socket.timeout:
            _LOGGER.debug(f"Read timeout from {self.ip}")
        except Exception as e:
            _LOGGER.debug(f"Error reading from {self.ip}: {e}")
        
        return None

    def _send_message(self, command):
        """Send message to device."""
        if not self._ensure_connection():
            return None

        try:
            payload = json.dumps(command) + "\r\n"
            self._socket.send(payload.encode('utf-8'))
            return self._read_response()
        except Exception as e:
            _LOGGER.debug(f"Failed to communicate with {self.ip}: {e}")
            self._close_connection()
            return None

    def send_command(self, state):
        """Send command to device."""
        command = {
            'cmd': CMD_SET,
            'pv': 0,
            'sn': self._get_sn(),
            'msg': {
                'attr': [1],
                'data': {
                    '1': 255 if state else 0
                }
            }
        }
        response = self._send_message(command)
        return response is not None and response.get('res') == 0

    def query_state(self):
        """Query device state."""
        command = {
            'cmd': CMD_QUERY,
            'pv': 0,
            'sn': self._get_sn(),
            'msg': {
                'attr': [0]
            }
        }
        response = self._send_message(command)
        if response and response.get('msg'):
            return response['msg'].get('data', {})
        return None
