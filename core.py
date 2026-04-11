# core.py

import sys
import os
import time
import copy
import serial
import re
import json
import random
import traceback
import sounddevice as sd
import queue
import threading
import logging
import librosa
import pyperclip
import pyaudiowpatch as pyaudio
import wave

from enum import Enum
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from config import Config

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# https://sematext.com/blog/python-logging/
# ✅ Bu modül her dosya için sadece bir import ile kullanılabilir:
# Örnek: `from core import *` veya `import core`

# ⚠️ Dikkat: PyQt6 komponentleri genellikle doğrudan kullanılmaz. Ama burada yapısal bir "kütüphane" olarak tutulur.
