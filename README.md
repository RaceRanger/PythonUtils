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


# AT Command Sequence Overview

This document outlines the AT commands used to configure and establish a secure MQTT connection on the modem. Each command is followed by a semicolon and a number indicating the response timeout (in seconds) expected after the command is sent.

---

## Command List and Descriptions

## MQTT_CONNECT.txt Summary

1. **`AT;1`**  
   **Description:**  
   Sends a basic AT command to test communication with the modem.  
   **Timeout:** 1 second

2. **`AT+QMTCFG="recv/mode",0,0,1;1`**  
   **Description:**  
   Configures the MQTT receive mode for client index 0. This command sets the mode (e.g., whether messages are buffered or delivered directly) using the specified parameters.  
   **Timeout:** 1 second

3. **`AT+QMTCFG="SSL",0,1,2;1`**  
   **Description:**  
   Configures the SSL settings for MQTT on client index 0. This command enables SSL (value 1) and associates it with a specific SSL profile (profile 2).  
   **Timeout:** 1 second

4. **`AT+QFLST;1`**  
   **Description:**  
   Lists all files stored in the modem’s file system (User File System, UFS).  
   **Timeout:** 1 second

5. **`AT+QFDEL="UFS:client.pem";1`**  
   **Description:**  
   Deletes the file `client.pem` from the modem's UFS, ensuring that any previous client certificate is removed before uploading a new one.  
   **Timeout:** 1 second

6. **`AT+QFDEL="UFS:cacert.pem";1`**  
   **Description:**  
   Deletes the file `cacert.pem` from the UFS to clear any old CA certificate before uploading an updated one.  
   **Timeout:** 1 second

7. **`AT+QFDEL="UFS:user_key.pem";1`**  
   **Description:**  
   Deletes the file `user_key.pem` from the UFS, clearing any previously stored user key.  
   **Timeout:** 1 second

8. **`AT+QFUPL="UFS:cacert.pem",1187,100;5`**  
   **Description:**  
   Uploads the CA certificate (`cacert.pem`) to the UFS. The command specifies a file size of 1187 bytes and a block size (or similar parameter) of 100.  
   **Timeout:** 5 seconds

9. **`AT+QFUPL="UFS:client.pem",1224,100;5`**  
   **Description:**  
   Uploads the client certificate (`client.pem`) to the UFS with a file size of 1224 bytes and a block size of 100.  
   **Timeout:** 5 seconds

10. **`AT+QFUPL="UFS:user_key.pem",1679,100;5`**  
    **Description:**  
    Uploads the user key (`user_key.pem`) to the UFS. The file is expected to be 1679 bytes in size, using a block size of 100.  
    **Timeout:** 5 seconds

11. **`AT+QSSLCFG="cacert",2,"UFS:cacert.pem";2`**  
    **Description:**  
    Configures the SSL engine by assigning the uploaded CA certificate (`cacert.pem`) to connection profile 2.  
    **Timeout:** 2 seconds

12. **`AT+QSSLCFG="clientcert",2,"UFS:client.pem";2`**  
    **Description:**  
    Configures the SSL engine to use the client certificate (`client.pem`) from the UFS for connection profile 2.  
    **Timeout:** 2 seconds

13. **`AT+QSSLCFG="clientkey",2,"UFS:user_key.pem";2`**  
    **Description:**  
    Configures the SSL engine to use the client key (`user_key.pem`) from the UFS for connection profile 2.  
    **Timeout:** 2 seconds

14. **`AT+QSSLCFG="seclevel",2,2;1`**  
    **Description:**  
    Sets the SSL security level for connection profile 2. A security level of 2 typically requires full certificate verification.  
    **Timeout:** 1 second

15. **`AT+QSSLCFG="sslversion",2,4;1`**  
    **Description:**  
    Specifies the SSL/TLS version to be used for connection profile 2. The value `4` might correspond to a specific TLS version (for example, TLS 1.2).  
    **Timeout:** 1 second

16. **`AT+QSSLCFG="ciphersuite",2,0xFFFF;1`**  
    **Description:**  
    Configures the cipher suite for connection profile 2. The parameter `0xFFFF` typically indicates a default or all-supported cipher suites.  
    **Timeout:** 1 second

17. **`AT+QSSLCFG="ignorelocaltime",2,1;1`**  
    **Description:**  
    Configures the SSL engine for connection profile 2 to ignore the local time validation during the SSL handshake. This can be useful if the device’s clock is not accurate.  
    **Timeout:** 1 second

18. **`AT+QMTCLOSE=0;4`**  
    **Description:**  
    Closes the existing MQTT connection for client index 0. This command ensures that any previous connection is properly terminated before establishing a new one.  
    **Timeout:** 4 seconds

19. **`AT+QMTOPEN=0,"a19qu3wt70ope2-ats.iot.ap-southeast-2.amazonaws.com",8883;15`**  
    **Description:**  
    Opens a new MQTT connection for client index 0. The command connects to the MQTT broker at `a19qu3wt70ope2-ats.iot.ap-southeast-2.amazonaws.com` on port `8883` (typically used for secure MQTT connections).  
    **Timeout:** 15 seconds

---

## Summary

This command sequence performs the following steps:

- **Initialization:**  
  It starts by issuing a basic AT command to confirm communication with the modem.

- **MQTT Configuration:**  
  It configures MQTT settings (including receive mode and SSL usage) to prepare the modem for secure communications.

- **File System Management:**  
  The sequence clears existing certificate files from the modem’s UFS and then uploads new certificate and key files required for establishing a secure connection.

- **SSL Configuration:**  
  After uploading the necessary files, it configures the SSL parameters for the connection, including certificates, security level, SSL/TLS version, and cipher suites.

- **MQTT Connection Management:**  
  The modem then closes any existing MQTT connection before opening a new secure connection to the specified MQTT broker.

By following this sequence, the modem is properly configured with SSL certificates and MQTT parameters to establish a secure connection to an MQTT broker, such as those used in IoT applications.

---

# AT Command Sequence for PDP Context Activation

This document outlines the AT commands used to set up and activate a PDP (Packet Data Protocol) context on a GSM/UMTS/LTE modem. Each command is appended with a semicolon and a timeout value (in seconds) indicating how long the modem should wait for a response.

---

## Command List and Descriptions

1. **`AT+CPIN?;1`**  
   **Description:**  
   Queries the SIM card status to determine whether it is ready, requires a PIN, or is in another state. This ensures that the SIM is properly initialized before attempting network operations.  
   **Timeout:** 1 second

2. **`AT+CGATT=1;1`**  
   **Description:**  
   Attaches the modem to the GPRS service. This command instructs the modem to register with the network for packet-switched data services.  
   **Timeout:** 1 second

3. **`AT+CGDCONT=1,"IP","onomondo";1`**  
   **Description:**  
   Defines a PDP context with a specified profile.  
   - **Profile ID:** 1  
   - **PDP Type:** "IP" (indicating an IP-based data connection)  
   - **APN:** "onomondo"  
   This command sets the data connection parameters necessary for establishing an internet connection.  
   **Timeout:** 1 second

4. **`AT+CGACT=1,1;1`**  
   **Description:**  
   Activates the PDP context defined in the previous step.  
   - The first parameter (1) indicates the PDP context identifier.  
   - The second parameter (1) commands the modem to activate the context.  
   This command initiates the data session using the defined settings.  
   **Timeout:** 1 second

5. **`AT+CGPADDR=1;1`**  
   **Description:**  
   Retrieves the IP address assigned to the activated PDP context (profile 1).  
   This command confirms that the PDP context is active and provides the IP address for further data communications.  
   **Timeout:** 1 second

---

## PDP_ACTIVATE.txt Summary

The command sequence performs the following tasks:

- **SIM Initialization:**  
  The modem checks the status of the SIM card using `AT+CPIN?`.

- **Network Attachment:**  
  The modem attaches to the network’s packet data service via `AT+CGATT=1`.

- **PDP Context Configuration:**  
  The modem sets up a PDP context with the specified APN (`onomondo`) using `AT+CGDCONT=1,"IP","onomondo"`.

- **PDP Context Activation:**  
  The context is activated with `AT+CGACT=1,1`, establishing a data session.

- **IP Address Retrieval:**  
  Finally, `AT+CGPADDR=1` confirms the session by retrieving the IP address assigned to the active PDP context.

Following this sequence ensures that the modem is correctly configured for data communication over the cellular network.
