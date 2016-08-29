from distutils.core import setup
import py2exe
setup(windows = ['winserver.py'], options={"py2exe":{"includes":["sip"]}})
