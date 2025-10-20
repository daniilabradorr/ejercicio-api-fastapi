#Añado la carpeta raíz del repo al sys.path para que "import app" funcione en CI, ya que me estaba dando error.
import os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)