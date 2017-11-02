import os
import subprocess
from datetime import datetime

ENV = os.getenv('ENV', 'local')
REV = subprocess.check_output(['git', 'rev-parse', 'HEAD']).strip()
STARTED = datetime.utcnow()
