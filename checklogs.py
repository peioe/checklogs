# -*- coding: utf-8 -*-
from sys import *
import os.path
import time
from optparse import OptionParser
import subprocess

# OPTIONS
wine_command = "wine"
checklogexe_path = "~/.wine/drive_c/Program Files/Exact Audio Copy/CheckLog.exe"

logs_goodlist = []
logs_badlist = []
logs_ignoredlist = []

def shellquote(s):
    return "'" + s.replace("'", "'\\''") + "'"

checklogexe_path = checklogexe_path.replace(" ", "\ ")

def process_log(log_full_path):
    global logs_goodlist, logs_badlist, logs_ignored_list, checklogexe_path
    log_full_path = log_full_path.replace(" ", "\ ")
    command = 'script -c "wine-development %s %s" tmpfile &> /dev/null' % (checklogexe_path, log_full_path)
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=None, shell=True)
    output = process.stdout.read()
    output = output.replace("\x1b[?1h\x1b=Log Integrity Checker   (C) 2010 by Andre Wiethoff\r\r\n\r\r\n1. ", "")
    output = output.replace("Script started, file is tmpfile\n", "")
    output = output.replace("\r\r\n\x1b[?1l\x1b>Script done, file is tmpfile\n", "")
    if output == "Log entry was modified, checksum incorrect!":
        logs_badlist.append(log_full_path)
    if output == "Log entry is fine!":
        logs_goodlist.append(log_full_path)
    if output == "Log entry has no checksum!":
        logs_ignoredlist.append(log_full_path)
    

def main():
    global logs_goodlist, logs_badlist, logs_ignored_list
    parser = OptionParser(usage="usage: %prog [options] top_directory")
    (options, args) = parser.parse_args()
    if len(args) < 1:
        parser.error("you need to specify a top directory")
    top_directory = args[0]
    print "Looking for .log files in %s ..." % top_directory
    
    found_logs = 0
    found_logs_list = []
    for root, dirs, files in os.walk(top_directory):
        for file in files:
            file_full_path = os.path.join(root, file)
            filename, file_extension = os.path.splitext(file_full_path)
            file_extension = file_extension.lower()
            if file_extension == ".log":
                found_logs += 1
                found_logs_list.append(file_full_path)
                
    print "Found %d logs. Running through CheckLog.exe ..." % found_logs
    for log in found_logs_list:
        process_log(log)
    print "Found %d good log(s), %d edited log(s) and skipped %d log(s) (no checksum)." % (len(logs_goodlist), len(logs_badlist), len(logs_ignoredlist))
    print "Good logs:"
    for log in logs_goodlist:
        print log
    print "Ignored logs (no checksum):"
    for log in logs_ignoredlist:
        print log
    print "BAD (edited) logs:"
    for log in logs_badlist:
        print log
    os.remove("tmpfile")
    
if __name__ == '__main__':
	main()

