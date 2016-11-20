#TWEleReceipt

This is a NCTU project for inspecting the Taiwan's Eletronic Receipt system.

#Installation

Python 2.7: `sudo apt-get install python, brew install python (OS X)`

Tesseract: `sudo apt-get install tesseract, brew install tesseract (OS X)`

`pip install image htmldom requests`


#Component
- Connector.py: to connect, get, post data
- HTMLDataResolver.py: for get the result from a .html
- ImageResolver.py: for captach resolver

#Usage
python Connector.py Receipt_ID DATE
