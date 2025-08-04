import psutil
import subprocess
from datetime import datetime

class MonitoringAgent:
    def get_metrics(self):
        return {
            "timestamp": datetime.now().isoformat(),
            "cpu": psutil.cpu_percent(interval=1),
            "memory": psutil.virtual_memory().percent,
            "disk": psutil.disk_usage('/').percent,
            "processes": len(psutil.pids())
        }

class LogAnalyzerAgent:
    def analyze(self, log_path="/var/log/system.log"):
        try:
            with open(log_path, 'r') as f:
                logs = f.readlines()[-100:]  # Last 100 lines
            
            return {
                "errors": [line.strip() for line in logs if "ERROR" in line],
                "warnings": [line.strip() for line in logs if "WARN" in line],
                "last_updated": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": str(e)}

class IncidentResponderAgent:
    def take_action(self, action_command):
        try:
            if "restart" in action_command.lower():
                service = action_command.split()[-1]
                result = subprocess.run(
                    ["sudo", "systemctl", "restart", service],
                    capture_output=True,
                    text=True
                )
                return {
                    "status": "success" if result.returncode == 0 else "failed",
                    "service": service,
                    "output": result.stdout,
                    "error": result.stderr
                }
            return {"status": "no_action_taken"}
        except Exception as e:
            return {"status": "error", "details": str(e)}