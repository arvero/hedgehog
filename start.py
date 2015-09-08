#! /usr/bin/python
# coding: utf8
#******************************************************************************
#*
#* (C) 2015 by arvero GmbH
#*
#*  arvero GmbH
#*  Winchesterstraße 2
#*  D-35394 Gießen
#*
#* ----------------------------------------------------------------------------
#* Module      : start.py
#*
#* Function    : Testscript for testing whole system as daemons
#*               (like ftp, http), APIs and applications.
#* Author      : Hubert
#* Date        : 2015-07-22
#*
#*
#* ----------------------------------------------------------------------------
#*
#******************************************************************************
import hedgehog
import sys
import os
import getopt

G_HOG = hedgehog.HedgeHog.instance()

CONFIG_NAME = "hedgehog.config"
OPTION_LIST = ["target", "ftpuser", "ftppass", "ftpport", "sline", "speed", "teluser", "telpass", "message", "control-log", "binpostfix"]

# options, influenced by command line arguments
showList = False
targetIp = None
ftpUser  = "ftp"
ftpPass  = "ftp"
ftpPort  = "21"
serialLine  = "/dev/ttyS0"
serialSpeed = "19200"
telUser = "tel"
telPass = "tel"
lastBootMsg = "Dummy_Last_Boot_Message"
binPostFix  = ""
controlLog  = None
moduleTestName = None
testcaseName   = None

# Check for a configuration file
if os.path.isfile(CONFIG_NAME) :
  cfgFile = open(CONFIG_NAME, "r")

  content = cfgFile.read()
  token = content.split("\n")

  for thisPair in token :
    nameValue = thisPair.split("=")
    if nameValue[0] != "" and nameValue[0] in OPTION_LIST :
      if nameValue[0] == "target" :
        targetIp = nameValue[1]
      elif nameValue[0] == "ftpuser" :
        ftpUser = nameValue[1]
      elif nameValue[0] == "ftppass" :
        ftpPass = nameValue[1]
      elif nameValue[0] == "ftpport" :
        ftpPort = nameValue[1]
      elif nameValue[0] == "sline" :
        serialLine = nameValue[1]
      elif nameValue[0] == "speed" :
        serialSpeed = nameValue[1]
      elif nameValue[0] == "teluser" :
        telUser = nameValue[1]
      elif nameValue[0] == "telpass" :
        telPass = nameValue[1]
      elif nameValue[0] == "message" :
        lastBootMsg = nameValue[1]
      elif nameValue[0] == "control-log" :
        controlLog = nameValue[1]
      elif nameValue[0] == "binpostfix" :
        binPostFix = nameValue[1]

else :
  print ""
  print "No configuration-file found, take default values"
  print ""

def usage() :
  print ""
  print "Usage: start.py <options> [module name [testcase name]]"
  print ""
  print "Options:"
  print "  -h, --help             show this help"
  print "  -l, --list             list all modules, or testcase if a module is given"
  print "  -t, --target=IPADDR    target IP address of testee"
  print "  -f, --ftpuser=NAME     username for ftp (default: ftp)"
  print "  -p, --ftppass=PASS     password for ftp (default: ftp)"
  print "  -o, --ftpport=PORT     port of ftp server (default: 21)"
  print "  -s, --sline=LINE       serial line to reach testee (default: /dev/ttyS0)"
  print "  -e, --speed=SPEED      speed of serial line (default: 19200)"
  print "  -u, --teluser=NAME     username for telnet (default: tel)"
  print "  -k, --telpass=PASS     password for telnet (default: tel)"
  print "  -m, --message=MSG      last boot message   (default: Dummy_Last_Boot_Message)"
  print "  -b, --postfix=POSTFIX  postfix of testbinary (default: No postfix)"
  print "  -c, --control-log=PATH path name of a log file that will contain all"
  print "                         communication between hedgehog and testee's"
  print "                         control console (e.g. starting and controling - or application-test"
  print "                         You could follow the testee's control console using tail"
  print "                         command in another terminal window, e.g. like below:"
  print ""
  print "                           $ tail -f <control log's path>"

# get command line attributes
try :
  opts, args = getopt.getopt(sys.argv[1:], "hlt:f:p:o:s:e:u:k:m:c:", ["help", "list", "target=", "ftpuser=", "ftppass=", "ftpport=", "sline=", "speed=", "teluser=", "telpass=", "message=", "postfix=", "control-log="])
except getopt.GetoptError as err :
    print str(err)
    usage()
    sys.exit(2)

# handle command line arguments
for o, a in opts :
  if o in ("-h", "--help") :
    usage()
    sys.exit()
  elif o in ("-l", "--list") :
    showList = True
  elif o in ("-t", "--target") :
    targetIp = a
  elif o in ("-f", "--ftpuser") :
    ftpUser = a
  elif o in ("-p", "--ftppass") :
    ftpPass = a
  elif o in ("-o", "--ftpport") :
    ftpPort = a
  elif o in ("-s", "--sline") :
    serialLine = a
  elif o in ("-e", "--speed") :
    serialSpeed = a
  elif o in ("-u", "--teluser") :
    telUser = a
  elif o in ("-k", "--telpass") :
    telPass = a
  elif o in ("-m", "--message") :
    lastBootMsg = a
  elif o in ("-b", "--postfix") :
    binPostFix = a
  elif o in ("-c", "--control-log") :
    controlLog = a
  else :
    assert False, "unhandled option"

# read module name / testcase name
if len(args) > 0 :
  moduleTestName = args[0]
if len(args) > 1 :
  testcaseName = args[1]

if showList :
  if moduleTestName == None :
    # show all modules
    print ""
    print "Available modules: "
    print G_HOG.get_module_names()
  elif testcaseName == None :
    print ""
    print "Available testcases in " + moduleTestName + ": "
    for testcase in G_HOG.get_testcases(moduleTestName) :
      print testcase
    print ""
else :
  if targetIp == None :
    print "missing target ip address"  
    usage()
    sys.exit(2)

  G_HOG.saveDefaultValues(targetIp, ftpUser, ftpPass, ftpPort, serialLine, serialSpeed, telUser, telPass, lastBootMsg, binPostFix)
  G_HOG.restoreFromDefaultValues()
  G_HOG.set_testeeControlLog(controlLog)
  G_HOG.process(moduleTestName, testcaseName)
