#!/usr/bin/env python3
import re
import requests
import argparse
import concurrent.futures
import os

# ANSI color codes for terminal output (optional)
class colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'

# Function to print HASH-buster in capital letters in dotted line
def print_banner():
    print('\033[1;97m' + '=' * 60)
    print('H  A  S  H  -  B  U  S  T  E  R'.center(60))
    print('=' * 60 + '\033[0m')

# Argument parser setup
parser = argparse.ArgumentParser()
parser.add_argument('-s', help='hash', dest='hash')
parser.add_argument('-f', help='file containing hashes', dest='file')
parser.add_argument('-d', help='directory containing hashes', dest='dir')
parser.add_argument('-t', help='number of threads', dest='threads', type=int)
args = parser.parse_args()

# Function definitions for hash cracking
def alpha(hashvalue, hashtype):
    return False

def beta(hashvalue, hashtype):
    response = requests.get('https://hashtoolkit.com/reverse-hash/?hash=' + hashvalue).text
    match = re.search(r'/generate-hash/\?text=(.*?)"', response)
    if match:
        return match.group(1)
    else:
        return False

def gamma(hashvalue, hashtype):
    response = requests.get('https://www.nitrxgen.net/md5db/' + hashvalue, verify=False).text
    if response:
        return response
    else:
        return False

def delta(hashvalue, hashtype):
    return False

def theta(hashvalue, hashtype):
    response = requests.get('https://md5decrypt.net/Api/api.php?hash=%s&hash_type=%s&email=deanna_abshire@proxymail.eu&code=1152464b80a61728' % (hashvalue, hashtype)).text
    if len(response) != 0:
        return response
    else:
        return False

# Main function to crack hashes
def crack(hashvalue):
    result = False
    if len(hashvalue) == 32:
        print ('Hash function : MD5')
        for api in [gamma, alpha, beta, theta, delta]:
            r = api(hashvalue, 'md5')
            if r:
                return r
    elif len(hashvalue) == 40:
        print ('Hash function : SHA1')
        for api in [alpha, beta, theta, delta]:
            r = api(hashvalue, 'sha1')
            if r:
                return r
    elif len(hashvalue) == 64:
        print ('Hash function : SHA-256')
        for api in [alpha, beta, theta]:
            r = api(hashvalue, 'sha256')
            if r:
                return r
    elif len(hashvalue) == 96:
        print ('Hash function : SHA-384')
        for api in [alpha, beta, theta]:
            r = api(hashvalue, 'sha384')
            if r:
                return r
    elif len(hashvalue) == 128:
        print ('Hash function : SHA-512')
        for api in [alpha, beta, theta]:
            r = api(hashvalue, 'sha512')
            if r:
                return r
    else:
        print ('This hash type is not supported.')
        return False

# Function for threaded execution
def threaded(hashvalue):
    resp = crack(hashvalue)
    if resp:
        print (hashvalue + ' : ' + resp)

# Function to process hashes from a directory
def grepper(directory):
    print (f"Searching hashes in directory: {directory}")
    try:
        results = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                if os.path.isfile(file_path):
                    with open(file_path, 'r') as f:
                        for line in f:
                            matches = re.findall(r'[a-f0-9]{128}|[a-f0-9]{96}|[a-f0-9]{64}|[a-f0-9]{40}|[a-f0-9]{32}', line.strip())
                            if matches:
                                for match in matches:
                                    results.append(match)
        print(f"Hashes found: {len(results)}")
        threadpool = concurrent.futures.ThreadPoolExecutor(max_workers=args.threads or 4)
        futures = (threadpool.submit(threaded, hashvalue) for hashvalue in results)
        for i, _ in enumerate(concurrent.futures.as_completed(futures)):
            if i + 1 == len(results) or (i + 1) % (args.threads or 4) == 0:
                print(f"Progress: {i + 1}/{len(results)}", end='\r')
    except KeyboardInterrupt:
        print("\nSearch interrupted.")

# Function to process hashes from a file
def miner(file):
    print (f"Cracking hashes from file: {file}")
    try:
        results = []
        with open(file, 'r') as f:
            for line in f:
                matches = re.findall(r'[a-f0-9]{128}|[a-f0-9]{96}|[a-f0-9]{64}|[a-f0-9]{40}|[a-f0-9]{32}', line.strip())
                if matches:
                    for match in matches:
                        results.append(match)
        print(f"Hashes found: {len(results)}")
        threadpool = concurrent.futures.ThreadPoolExecutor(max_workers=args.threads or 4)
        futures = (threadpool.submit(threaded, hashvalue) for hashvalue in results)
        for i, _ in enumerate(concurrent.futures.as_completed(futures)):
            if i + 1 == len(results) or (i + 1) % (args.threads or 4) == 0:
                print(f"Progress: {i + 1}/{len(results)}", end='\r')
    except FileNotFoundError:
        print(f"Error: File '{file}' not found.")
    except KeyboardInterrupt:
        print("\nCracking interrupted.")

# Function to process a single hash
def single(args):
    result = crack(args.hash)
    if result:
        print (result)
    else:
        print ('Hash was not found in any database.')

# Execution based on command-line arguments
if __name__ == "__main__":
    if args.dir:
        grepper(args.dir)
    elif args.file:
        miner(args.file)
    elif args.hash:
        single(args)
    else:
        print_banner()
        print ('Please specify a hash (-s), file (-f), or directory (-d) to proceed.')
