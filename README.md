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

Edit your COM port, baud rate can remain the same.

```python .\modem_main.py```

## Tests

To run tests run:

```python -m unittest discover -s tests```


# AT Command Sequence Overview

This document outlines the AT commands used to configure and establish a secure MQTT connection on the modem and to activate a PDP (Packet Data Protocol) context for cellular data communication. Each command is followed by a semicolon and a number indicating the response timeout (in seconds) expected after the command is sent.

---

## MQTT Connection Sequence (MQTT_CONNECT.txt)

This sequence configures the modem for secure MQTT communication, including SSL setup and certificate management.

### Command List and Descriptions

| **Command**                                                                                                 | **Description**                                                                                                                                                      | **Timeout** |
| ----------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------- |
| `AT;1`                                                                                                      | Tests basic communication with the modem.                                                                                                                          | 1 sec       |
| `AT+QMTCFG="recv/mode",0,0,1;1`                                                                               | Configures the MQTT receive mode for client 0. Sets the mode (e.g., whether messages are buffered or delivered directly) using specified parameters.                 | 1 sec       |
| `AT+QMTCFG="SSL",0,1,2;1`                                                                                     | Enables SSL for MQTT on client 0 and associates it with SSL profile 2.                                                                                               | 1 sec       |
| `AT+QFLST;1`                                                                                                | Lists all files stored in the modem’s User File System (UFS).                                                                                                        | 1 sec       |
| `AT+QFDEL="UFS:client.pem";1`                                                                                 | Deletes the `client.pem` file from the UFS, ensuring that any previous client certificate is removed before uploading a new one.                                      | 1 sec       |
| `AT+QFDEL="UFS:cacert.pem";1`                                                                                 | Deletes the `cacert.pem` file from the UFS to clear any old CA certificate before uploading an updated one.                                                         | 1 sec       |
| `AT+QFDEL="UFS:user_key.pem";1`                                                                               | Deletes the `user_key.pem` file from the UFS, clearing any previously stored user key.                                                                               | 1 sec       |
| `AT+QFUPL="UFS:cacert.pem",1187,100;5`                                                                         | Uploads the CA certificate (`cacert.pem`) to the UFS. Specifies a file size of 1187 bytes and a block size (or similar parameter) of 100.                           | 5 sec       |
| `AT+QFUPL="UFS:client.pem",1224,100;5`                                                                         | Uploads the client certificate (`client.pem`) to the UFS with a file size of 1224 bytes and a block size of 100.                                                     | 5 sec       |
| `AT+QFUPL="UFS:user_key.pem",1679,100;5`                                                                       | Uploads the user key (`user_key.pem`) to the UFS, expected to be 1679 bytes, with a block size of 100.                                                                | 5 sec       |
| `AT+QSSLCFG="cacert",2,"UFS:cacert.pem";2`                                                                    | Configures the SSL engine by assigning the uploaded CA certificate (`cacert.pem`) to connection profile 2.                                                           | 2 sec       |
| `AT+QSSLCFG="clientcert",2,"UFS:client.pem";2`                                                                  | Configures the SSL engine to use the client certificate (`client.pem`) from the UFS for connection profile 2.                                                         | 2 sec       |
| `AT+QSSLCFG="clientkey",2,"UFS:user_key.pem";2`                                                                 | Configures the SSL engine to use the client key (`user_key.pem`) from the UFS for connection profile 2.                                                               | 2 sec       |
| `AT+QSSLCFG="seclevel",2,2;1`                                                                                   | Sets the SSL security level for connection profile 2, typically requiring full certificate verification.                                                            | 1 sec       |
| `AT+QSSLCFG="sslversion",2,4;1`                                                                                 | Specifies the SSL/TLS version to be used for connection profile 2. The value `4` might correspond to a specific TLS version (e.g., TLS 1.2).                         | 1 sec       |
| `AT+QSSLCFG="ciphersuite",2,0xFFFF;1`                                                                           | Configures the cipher suite for connection profile 2. The parameter `0xFFFF` typically indicates a default or all-supported cipher suites.                              | 1 sec       |
| `AT+QSSLCFG="ignorelocaltime",2,1;1`                                                                            | Instructs connection profile 2 to ignore local time validation during the SSL handshake, useful if the device’s clock is not accurate.                                | 1 sec       |
| `AT+QMTCLOSE=0;4`                                                                                             | Closes the existing MQTT connection for client 0, ensuring any previous connection is properly terminated.                                                          | 4 sec       |
| `AT+QMTOPEN=0,"a19qu3wt70ope2-ats.iot.ap-southeast-2.amazonaws.com",8883;15`                                   | Opens a new secure MQTT connection for client 0 to the specified broker on port 8883.                                                                                | 15 sec      |

### Summary of MQTT Connection Sequence

- **Initialization:** Tests communication with the modem.
- **MQTT Configuration:** Sets the receive mode and enables SSL for secure communication.
- **File Management:** Clears existing certificate files and uploads new certificates and keys.
- **SSL Setup:** Configures SSL parameters including certificates, security level, TLS version, and cipher suites.
- **Connection Management:** Closes any existing MQTT connection and opens a new secure connection to the broker.

---

## PDP Context Activation Sequence (PDP_ACTIVATE.txt)

This sequence sets up and activates a PDP (Packet Data Protocol) context for cellular data communication.

### Command List and Descriptions

| **Command**                       | **Description**                                                                                                                                                       | **Timeout** |
| --------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------- |
| `AT+CPIN?;1`                      | Queries the SIM card status to determine if it is ready, requires a PIN, or is in another state.                                                                      | 1 sec       |
| `AT+CGATT=1;1`                    | Attaches the modem to the GPRS network by registering for packet-switched data services.                                                                             | 1 sec       |
| `AT+CGDCONT=1,"IP","onomondo";1`   | Defines PDP context 1 with an IP data connection and APN "onomondo", setting the necessary parameters for internet connectivity.                                    | 1 sec       |
| `AT+CGACT=1,1;1`                  | Activates PDP context 1 to initiate the data session.                                                                                                               | 1 sec       |
| `AT+CGPADDR=1;1`                  | Retrieves the IP address assigned to the activated PDP context, confirming that the data session is active.                                                            | 1 sec       |

### Summary of PDP Context Activation Sequence

- **SIM Initialization:** Verifies SIM readiness using `AT+CPIN?`.
- **Network Attachment:** Attaches to the network’s data service with `AT+CGATT=1`.
- **PDP Setup:** Configures PDP context 1 with the APN "onomondo" via `AT+CGDCONT=1,"IP","onomondo"`.
- **PDP Activation:** Activates the context using `AT+CGACT=1,1`.
- **IP Retrieval:** Confirms the data session by retrieving the IP address with `AT+CGPADDR=1`.

---

By following these sequences, the modem is configured for both secure MQTT communication and cellular data connectivity, ensuring reliable IoT communication for RaceRanger's automated systems.
