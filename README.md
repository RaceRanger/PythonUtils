# PythonUtils
A set of python scripts used for task automation throughout RaceRanger

## Setup

Clone the repo
```git clone https://github.com/RaceRanger/PythonUtils.git```

Go to root
```cd PythonUtils```

Create venv
```python -m venv myenv```

Activate venv
```./myenv/Scripts/activate```

Install deps
```pip install -r requirements.txt```

## Usage

### Modem Translator

Edit the commands.txt file with the AT commands you wish to send to the modem. 
These commands should be seperated by a new line. See commands.txt for example.

Edit your COM port, baud rate can remain the same.

Save all files and run

```python .\modem_translator.py```
