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
The translator can be run in two configurations, either the commands will be ran from the commands.txt file, or the commands can be used as arguments into the script. The commands are sent one-by-one to the serial port of the users choice. Once a response is recived, the next command is transmitted until the entire command file has been parsed. If a command fails, it is logged at the bottom of the page. 

Edit the commands.txt file with the AT commands you wish to send to the modem. 
These commands should be seperated by a new line. See commands.txt for example.

Edit your COM port, baud rate can remain the same.

To run using the commands in the commands.txt run:

```python .\modem_translator.py```

To run using the commands from the arguments run:

```python .\utils\modem_translator.py "EXAMPLE_CMD1" "EXAMPLE_CMD2"...```

## Tests

To run tests run:

```python -m unittest discover -s tests```
