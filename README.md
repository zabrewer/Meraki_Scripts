# Meraki_Scripts

This repo consists of various Meraki scripts I have written that don't belong anywhere else.  I'll add more in the future as time allows.

Current scripts include:

* [claim_licenses.py](claim_licenses.py) - simple script that claims all meraki licenses in a CSV file.  Could be modified for SNs or other attributes.  Dependencies include the meraki python module (pip install meraki) and requests module.  See the example [licenses.csv](licenses.csv) for how the CSV should be structured