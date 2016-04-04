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
logs_xldlist = []
logs_errorlist = []

def shellquote(s):
    return "'" + s.replace("'", "'\\''") + "'"

checklogexe_path = checklogexe_path.replace(" ", "\ ")

def process_log(log_full_path):
    global logs_goodlist, logs_badlist, logs_ignored_list, logs_errorlist, checklogexe_path
    log_full_path = log_full_path.replace(" ", "\ ")
    log_full_path = log_full_path.replace("(", "\(")
    log_full_path = log_full_path.replace("'", "\\\'")
    log_full_path = log_full_path.replace(")", "\)")
    log_full_path = log_full_path.replace("&", "\&")
    command = 'script -q -c "wine-development %s %s" /dev/null' % (checklogexe_path, log_full_path)
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=None, shell=True)
    output = process.stdout.read()
    if "Log entry has no checksum!" in output:
        logs_ignoredlist.append(log_full_path)
    elif "Log entry was modified, checksum incorrect!" in output:
        logs_badlist.append(log_full_path)
    elif "Log entry is fine!" in output:
        logs_goodlist.append(log_full_path)
    else:
        logs_errorlist.append(log_full_path)

def main():
    global logs_goodlist, logs_badlist, logs_ignored_list, logs_errorlist, logs_xldlist
    parser = OptionParser(usage="usage: %prog [options] top_directory")
    parser.add_option("-i", "--ignore-ac", action="store_false", dest="ignore_ac", default=True,
                  help="ignore logs named 'audiochecker.log'(default is True)")

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
            if file_extension == ".log" and not "audiochecker.log" in file:
                fo = open(file_full_path, 'r')
                content = fo.read()
                found_logs += 1
                if "X Lossless Decoder version" in content:
                    logs_xldlist.append(file_full_path)
                else:
                    found_logs_list.append(file_full_path)
                
    print "Found %d logs. Running through CheckLog.exe ..." % found_logs
    for log in found_logs_list:
        process_log(log)
    print "Found %d good log(s), %d edited log(s) and skipped %d log(s) (%d XLD logs and %d had no checksum)." % (len(logs_goodlist), len(logs_badlist), len(logs_ignoredlist)+len(logs_xldlist), len(logs_xldlist), len(logs_ignoredlist))
    logs_goodlist.sort()
    logs_badlist.sort()
    logs_ignoredlist.sort()
    logs_errorlist.sort()
    logs_xldlist.sort()
    if len(logs_xldlist) != 0:
        print "XLD logs (ignored):"
        for log in logs_xldlist:
            print log
    if len(logs_goodlist) != 0:
        print "Good logs:"
        for log in logs_goodlist:
            print log
    if len(logs_ignoredlist) != 0:
        print "Ignored logs (no checksum):"
        for log in logs_ignoredlist:
            print log
    if len(logs_badlist) != 0:
        print "BAD (edited) logs:"
        for log in logs_badlist:
            print log
    if len(logs_errorlist) != 0:
        print "There was an error while processing:"
        for log in logs_errorlist:
            print log
    
if __name__ == '__main__':
	main()

