import os
import subprocess


ENV = os.getenv('ENV', 'local')
REV = subprocess.check_output(['git', 'rev-parse', 'HEAD']).strip()
