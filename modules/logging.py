# wordpress_bruteforce/modules/logging.py
import json
from datetime import datetime


class Logger:
    """Enhanced logging system"""

    def __init__(self):
        self.success_file = "data/successful_logins.json"
        self.error_file = "data/error_logs.json"

    def log_success(self, username, password):
        """Log successful login attempts"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "username": username,
            "password": password,
            "type": "xmlrpc_bruteforce",
        }
        self._write_log(entry, self.success_file)

    def log_error(self, error_type, details):
        """Log system errors"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "error_type": error_type,
            "details": details,
        }
        self._write_log(entry, self.error_file)

    def _write_log(self, entry, filename):
        """Generic log writing method"""
        try:
            with open(filename, "a") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception as e:
            print(f"⚠️ Logging error: {str(e)}")
