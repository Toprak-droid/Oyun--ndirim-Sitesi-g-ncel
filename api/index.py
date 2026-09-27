import sys
import os

# Kök dizindeki main.py dosyasını görebilmesi için yolu ekler
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app