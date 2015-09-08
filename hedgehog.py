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
#* Module      : hedgehog.py
#*
#* Function    : This module contains the main managing functionality of
#*               hedgehog.
#* Author      : Hubert
#* Date        : 2015-07-22
#*
#*
#* ----------------------------------------------------------------------------
#*
#******************************************************************************

from singleton import Singleton
from ftplib import FTP
from shutil import copy
import moduleList
import ConfigParser
import serial
import re
import sys
import os
from time import sleep
import module.moduletest

defaultTargetIp = None
defaultFtpUser  = None
defaultFtpPass  = None
defaultFtpPort  = None
defaultSerialLine  = None
defaultSerialSpeed = None
defaultTelUser = None
defaultTelPass = None
defaultLastBootMsg = None
defaultBinPostFix  = None

@Singleton
class HedgeHog :

  #################
  # Public Methods
  #################

  ##############################################################################
  #
  #  Method:
  #    log()
  #
  #  Description:
  #    Logs some message
  #
  #  Parameters:
  #    status  - "ERROR", "WARNING" or "INFO"
  #    message - message to log
  #
  #  Return:
  #    -
  #
  ##############################################################################

  def log(self, status, message) :
    if status == "ERROR" :
      print '\033[1;31m' + status + ": " + message + '\033[1;m'
    elif status == "INFO" :
      print '\033[1;32m' + status + ": " + message + '\033[1;m'
    elif status == "WARNING" :
      print '\033[1;33m' + status + ": " + message + '\033[1;m'

  ##############################################################################
  #
  #  Method:
  #    fileSend()
  #
  #  Description:
  #    Transfers a file to the testee.
  #
  #  Parameters:
  #    srcPath - local source Path of the file
  #    dstPath - remote destination path (relative to virtual root dir)
  #
  #  Return:
  #    -
  #
  ##############################################################################

  def fileSend(self, srcPath, dstPath) :
    self.transferfile("put", srcPath, dstPath)

  ##############################################################################
  #
  #  Method:
  #    fileRetrieve()
  #
  #  Description:
  #    Retrieves a file from the testee.
  #
  #  Parameters:
  #    srcPath - local source Path of the file
  #    dstPath - remote destination path (relative to virtual root dir)
  #
  #  Return:
  #    -
  #
  ##############################################################################

  def fileRetrieve(self, srcPath, dstPath) :
    self.transferfile("get", srcPath, dstPath)

  ##############################################################################
  #
  #  Method:
  #    remoteShellSend()
  #
  #  Description:
  #    Sends a cmdline to the remote command shell
  #
  #  Parameters:
  #    cmdline - a command line given as a string
  #
  #  Return:
  #   - 
  #
  ##############################################################################

  def remoteShellSend(self, cmdline) :
    if self.__useTelnet == 1 :
      # TODO: implement
      pass
    else :
      self.serial_Client.write(cmdline)
      if self.__testeeCtrlLogFile :
        # log to serial-receive logfile
        self.__testeeCtrlLogFile.write(cmdline)
        self.__testeeCtrlLogFile.flush()

  ##############################################################################
  #
  #  Method:
  #    remoteShellReceive()
  #
  #  Description:
  #    Waits for a matching cmdline from the remote command shell.
  #
  #  Parameters:
  #    regExpr - optional regular expression for matching the cmdline. If 
  #              regExpr is None the next receive cmdline will match.
  #    timeout - seconds until method returns, default is 3 seconds
  #
  #  Return:
  #    Matching cmdline 
  #    "None" if timeout
  #
  ##############################################################################

  def remoteShellReceive(self, regExpr, timeout) :
    time = 0.0
    read_string = ""
    if timeout == None :
      timeout = 3.0

    if self.__useTelnet == 1 :
      # TODO: implement
      pass
    else :
      # do-while-loop in python
      while True :
        # we have to compare "less than" because its not possible to compare
        # floats of equavalence maybe because of its representation 
        time += 0.1
        if timeout < time :
          return None

        read_string += self.serial_Client.readline() # read a '\n' terminating line

        if re.search("Segmentation fault", read_string) != None :
          self.log("WARNING", "Segmentation fault while waiting on \"" + regExpr + "\"")

        if read_string != "" and read_string[len(read_string)-1] == '\n' :
          # a complete line was received
          if self.__testeeCtrlLogFile :
            # log to serial-receive logfile
            self.__testeeCtrlLogFile.write(read_string)
            self.__testeeCtrlLogFile.flush()
          read_string = read_string[:-1] # cut '\n'
          while read_string != "" and read_string[len(read_string)-1] == '\r' :
            read_string = read_string[:-1] # cut '\r'
          if regExpr == None :
            return read_string
          elif re.search(regExpr, read_string) != None :
            return read_string
          else :
            read_string = "" # no match, wait for next line

        else :
          sleep(0.1) # 100 ms

  ##############################################################################
  #
  #  Method:
  #    remoteShellClearRecvBuffer()
  #
  #  Description:
  #    Wait until everything is sent to remote shell   
  #
  #  Parameters:
  #    - 
  #
  #  Return:
  #    -
  #
  ##############################################################################

  def remoteShellClearRecvBuffer(self) :
    self.serial_Client.flushInput()

  #############################
  # Private/Protected Methods
  #############################

  ##############################################################################
  #
  #  Method:
  #    __init__
  #
  #  Description:
  #    Creates an instance of the class.
  #
  #  Parameters:
  #    -
  #
  #  Return:
  #    -
  #
  ##############################################################################

  def __init__(self) :
    global defaultTargetIp
    global defaultFtpUser
    global defaultFtpPass
    global defaultFtpPort
    global defaultSerialLine
    global defaultSerialSpeed
    global defaultTelUser
    global defaultTelPass
    global defaultLastBootMsg
    self.__targetIP  = defaultTargetIp
    self.__useNFS    = 0
    self.__ftpUser   = defaultFtpUser
    self.__ftpPasswd = defaultFtpPass
    self.__ftpPort   = defaultFtpPort
    self.__serialLine  = defaultSerialLine
    self.__serialSpeed = defaultSerialSpeed
    self.__useTelnet   = 0
    self.__telnetUser  = defaultTelUser
    self.__telnetPasswd = defaultTelPass
    self.__errors = 0
    self.__failed_testcases = []
    self.__testeeCtrlLogFile = None
    self.__moduletests = None
    self.__defaultLastBootMsg = defaultLastBootMsg

  ##############################################################################
  #
  #  Method:
  #    process()
  #
  #  Description:
  #    Iterates through all modules from self.get_modules() and calls their
  #    process()-method. Close connection of serial port at the end.
  #
  #  Parameters:
  #    moduleTestName - name of the module test that should be processed. If
  #                     name is None or empty all module tests are processed.
  #    testcaseName   - name of the testcase which hve to be executed
  #
  #  Return:
  #    -
  #
  ##############################################################################

  def process(self, moduleTestName, testcaseName) :

    if self.__testeeCtrlLogFilePath != None :
      self.__testeeCtrlLogFile = open(self.__testeeCtrlLogFilePath, 'w')

    if moduleTestName == None or moduleTestName == "" :
      for this_module in self.get_modules() :
        Module = this_module
        self.log("INFO", "___________________")
        self.log("INFO", "Module: " + Module.getName())
        Module.enter()
        Module.process(testcaseName)
        Module.leave()
    else :
      for this_module in self.get_modules() :
        # Get argument of self.get_modules() and cast to string
        string = str(this_module)
        # Look if this_module is the needed one defined in moduleTestName
        if moduleTestName in string :
          Module = this_module
          self.log("INFO", "___________________")
          self.log("INFO", "Module: " + Module.getName())
          Module.enter()
          Module.process(testcaseName)
          Module.leave()

    # Print Errors if there were some
    self.log("INFO",  "___________________\n")
    if self.__errors > 0 :
      self.log("ERROR",  str(self.__errors) + " errors occurred: ")
      self.log("ERROR", "These testcases had failed: \n\n" + str(self.__failed_testcases) + "\n")

    self.log("INFO",  "All tests finished")
    self.log("INFO",  "___________________")

    # At the end of all tests the serial port connection have to be closed
    self.serial_Client.close()

    if self.__testeeCtrlLogFile != None :
      self.__testeeCtrlLogFile.close()

  ##############################################################################
  #
  #  Method:
  #    add_error()
  #
  #  Description:
  #    Adds an error and the name of the failed testcases to a list   
  #
  #  Parameters:
  #    name - The name of the failed testcase
  #
  #  Return:
  #    -
  #
  ##############################################################################

  def add_error(self, name) :
    self.__errors += 1
    self.__failed_testcases.append(name)

  ##############################################################################
  #
  #  Method:
  #    set_iniString()
  #
  #  Description:
  #    Sets <Ini-File>.INI parameters, e.g. [SECTION] Name = Value.
  #    Existing content will stay but duplicate contents will be overwritten   
  #
  #  Parameters:
  #    Ininame - Name of the INI-File 
  #    section - Section which have to be set [SECTION]
  #    name    - Name of the parameter
  #    value   - Value of the parameter
  #
  #  Return:
  #    -
  #
  ##############################################################################

  def set_iniString(self, Ininame, section, name, value) :
    ini = ConfigParser.RawConfigParser()
    try :
      ini.read(Ininame)
    except :
      ini.add_section(section)

    if not ini.has_section(section) :
      # unreachable, but...!
      ini.add_section(section)

    ini.set(section, name, value)

    with open(Ininame, 'w') as inifile :
      ini.write(inifile)
      inifile.close()

  ##############################################################################
  #
  #  Method:
  #    transferfile()
  #
  #  Description:
  #    Transfer a source-file to a destination-path.    
  #    Either via NFS or FTP
  #
  #  Parameters:
  #    srcPath - Source Path as a string
  #    dstPath - Destination Path as a string
  #
  #  Return:
  #    -
  #
  ##############################################################################

  def transferfile(self, operation, srcPath, dstPath) :
    if self.__useNFS == 1 :
      self.transferfilenfs(operation, srcPath, dstPath)
    else :
      self.transferfileftp(operation, srcPath, dstPath)

  ##############################################################################
  #
  #  Method:
  #    transferfilenfs()
  #
  #  Description:
  #    Copy a source-file to a destination-path via NFS.
  #
  #  Parameters:
  #    srcPath   - Absolute source Path as a string
  #    dstPath   - Absoulte destination Path as a string
  #
  #  Return:
  #    - 
  #
  ##############################################################################

  def transferfilenfs(self, srcPath, dstPath) :
    if operation == 'put' :
      # TODO: use environment variable for NFS root path
      copy(srcPath, dstPath)

  ##############################################################################
  #
  #  Method:
  #    transferfileftp()
  #
  #  Description:
  #    Copy a source-file to a destination-path via FTP.
  #
  #  Parameters:
  #   operation - "put", sends the file to target
  #               "get", retrieves the file from the target
  #   srcPath   - Source Path as a string
  #   dstPath   - Destination Path as a string
  #
  #  Return:
  #   - 
  #
  ##############################################################################

  def transferfileftp(self, operation, srcPath, dstPath) :
    # Connect with destination FTP-Server
    try :
      Client = FTP()
      Client.connect(self.__targetIP, self.__ftpPort)
      Client.login(self.__ftpUser, self.__ftpPasswd)
      # Change directory to destination and put file
      if operation == 'put' :
        Client.storbinary("STOR " + dstPath ,open(srcPath, 'r'))
      else :
        Client.retrbinary("RETR " + srcPath ,open(dstPath, 'wb').write)
      # Close Connection to server
      Client.quit()
    except Exception, e :
      if operation == 'put' :
        self.log("ERROR",  "Could not send file via FTP.")
        self.log("ERROR",  "Local path : " + srcPath)
        self.log("ERROR",  "Remote path: " + dstPath)
        # No need anymore for that binary
        os.remove(srcPath)
      else :
        self.log("ERROR",  "Could not retrieve file via FTP.")
        self.log("ERROR",  "Local path : " + dstPath)
        self.log("ERROR",  "Remote path: " + srcPath)
      self.log("ERROR",  "Username   : " + self.__ftpUser)
      self.log("ERROR",  "Password   : " + self.__ftpPasswd)
      self.log("ERROR",  "Target IP  : " + self.__targetIP)
      self.log("ERROR",  "FTP Failure: " + str(e))
      sys.exit(1)

  ##############################################################################
  #
  #  Method:
  #    set_testeeControlLog
  #
  #  Description:
  #    Sets the path of the text file that will contain all communiation between 
  #    hedgehog and testee control console (e.g. starting API tests).
  #
  #  Parameters:
  #    path - path to log file, if path is None (by default) the log file will
  #           not be created.
  #
  #  Return:
  #    -
  #
  ##############################################################################

  def set_testeeControlLog(self, path) :
    self.__testeeCtrlLogFilePath = path

  ##############################################################################
  #
  #  Method:
  #    reset_targetIP()
  #
  #  Description:
  #    Set Target-IP to initial value
  #
  #  Parameters:
  #    -
  #
  #  Return:
  #    -
  #
  ##############################################################################

  def reset_targetIP(self) :
    self.__targetIP = self.__originalTargetIP

  ###############################
  # Getter- and Setter - Methods
  ###############################

  ##############################################################################
  #
  #  Method:
  #    set_targetIP()
  #
  #  Description:
  #    Set new Target-IP    
  #
  #  Parameters:
  #    newVal - A new IP given as a string
  #
  #  Return:
  #    -
  #
  ##############################################################################

  def set_targetIP(self, newVal) :
    if self.__targetIP == None :
      self.__originalTargetIP = newVal
    self.__targetIP = newVal

  ##############################################################################
  #
  #  Method:
  #    set_useNFS()
  #
  #  Description:
  #    Decision between using NFS to transfer files or not     
  #
  #  Parameters:
  #    newVal - "0" for not using NFS, something else for use
  #
  #  Return:
  #    -
  #
  ##############################################################################

  def set_useNFS(self, newVal) :
    if newVal == "0" :
      self.__useNFS = 0
    else :
      self.__useNFS = 1

  ##############################################################################
  #
  #  Method:
  #    set_ftpUser()
  #
  #  Description:
  #    Username for login issues via FTP     
  #
  #  Parameters:
  #    newVal - Username given as a string
  #
  #  Return:
  #    -
  #
  ##############################################################################

  def set_ftpUser(self, newVal) :
    self.__ftpUser = str(newVal)

  ##############################################################################
  #
  #  Method:
  #    set_ftpPasswd()
  #
  #  Description:
  #    Sets a new Password for login issues via FTP      
  #
  #  Parameters:
  #    newVal - Password given as a string
  #
  #  Return:
  #    -
  #
  ##############################################################################

  def set_ftpPasswd(self, newVal) :
    self.__ftpPasswd = str(newVal)

  ##############################################################################
  #
  #  Method:
  #    serialLine()
  #
  #  Description:
  #    Sets a new serial line      
  #
  #  Parameters:
  #    newVal - Line given as a string
  #
  #  Return:
  #    -
  #
  ##############################################################################

  def set_serialLine(self, newVal) :
    self.__serialLine = str(newVal)
    self.serial_Client.close()
    self.serial_Client = serial.Serial(self.__serialLine, self.__serialSpeed, timeout=0)

  ##############################################################################
  #
  #  Method:
  #    serialSpeed()
  #
  #  Description:
  #    Sets a new serial speed    
  #
  #  Parameters:
  #    newVal - Port given as a string
  #
  #  Return:
  #    -
  #
  ##############################################################################

  def set_serialSpeed(self, newVal) :
    if newVal > 0 :
      self.__serialSpeed = newVal
      self.serial_Client.close()
      self.serial_Client = serial.Serial(self.__serialLine, self.__serialSpeed, timeout=0)

  ##############################################################################
  #
  #  Method:
  #    ftpPort()
  #
  #  Description:
  #    -
  #
  #  Parameters:
  #    newVal - Port given as a string
  #
  #  Return:
  #    -
  #
  ##############################################################################

  def set_ftpPort(self, newVal) :
    if newVal > 0 :
      self.__ftpPort = newVal

  ##############################################################################
  #
  #  Method:
  #    set_useTelnet()
  #
  #  Description:
  #    Desicion between using Telnet
  #
  #  Parameters:
  #    newVal - "0" for not using Telnet, something else for use
  #
  #  Return:
  #    -
  #
  ##############################################################################

  def set_useTelnet(self, newVal) :
    if newVal == "0" :
      self.__useTelnet = 0
    else :
      self.__useTelnet = 1

  ##############################################################################
  #
  #  Method:
  #    set_telnetUser()
  #
  #  Description:
  #    Sets a new username for telnet login
  #
  #  Parameters:
  #    newVal - new username given as a string
  #
  #  Return:
  #    -
  #
  ##############################################################################

  def set_telnetUser(self, newVal) :
    self.__telnetUser = str(newVal)

  ##############################################################################
  #
  #  Method:
  #    set_telnetPasswd()
  #
  #  Description:
  #    Sets a new password for telnet login
  #
  #  Parameters:
  #    newVal - new password given as a string
  #
  #  Return:
  #    -
  #
  ##############################################################################

  def set_telnetPasswd(self, newVal) :
    self.__telnetPasswd = str(newVal)

  ##############################################################################
  #
  #  Method:
  #    set_lastBootMsg()
  #
  #  Description:
  #    Last boot message
  #
  #  Parameters:
  #    newVal - Last boot message given as a string
  #
  #  Return:
  #    -
  #
  ##############################################################################

  def set_lastBootMsg(self, newVal) :
    self.__lastBootMsg = str(newVal)

  ##############################################################################
  #
  #  Method:
  #    set_binPostFix()
  #
  #  Description:
  #    Sets the new postfix of test binary
  #
  #  Parameters:
  #    newVal - New postfix of test binary
  #
  #  Return:
  #    -
  #
  ##############################################################################

  def set_binPostFix(self, newVal) :
    self.__binPostFix = str(newVal)

  ##############################################################################
  #
  #  Method:
  #    saveDefaultValues()
  #
  #  Description:
  #    Saves the default values for hedgehog
  #
  #  Parameters:
  #    -
  #
  #  Return:
  #    -
  #
  ##############################################################################

  def saveDefaultValues(self, targetIp, ftpUser, ftpPass, ftpPort, serialLine, serialSpeed, telUser, telPass, lastBootMsg, binPostFix) :
    global defaultTargetIp
    global defaultFtpUser
    global defaultFtpPass
    global defaultFtpPort
    global defaultSerialLine
    global defaultSerialSpeed
    global defaultTelUser
    global defaultTelPass
    global defaultLastBootMsg
    global defaultBinPostFix
    defaultTargetIp = targetIp
    defaultFtpUser = ftpUser
    defaultFtpPass = ftpPass
    defaultFtpPort = ftpPort
    defaultTelUser = telUser
    defaultTelPass = telPass
    defaultSerialLine  = serialLine
    defaultSerialSpeed = serialSpeed
    defaultLastBootMsg = lastBootMsg
    defaultBinPostFix = binPostFix

  ##############################################################################
  #
  #  Method:
  #    restoreFromDefaultValues()
  #
  #  Description:
  #    Restores hedgehog's config from default values
  #
  #  Parameters:
  #    -
  #
  #  Return:
  #    -
  #
  ##############################################################################

  def restoreFromDefaultValues(self) :
    global defaultTargetIp
    global defaultFtpUser
    global defaultFtpPass
    global defaultFtpPort
    global defaultSerialLine
    global defaultSerialSpeed
    global defaultTelUser
    global defaultTelPass
    global defaultLastBootMsg
    global defaultBinPostFix
    self.__targetIP  = defaultTargetIp
    self.__ftpUser   = defaultFtpUser
    self.__ftpPasswd = defaultFtpPass
    self.__ftpPort   = defaultFtpPort
    self.__telnetUser  = defaultTelUser
    self.__telnetPasswd = defaultTelPass
    self.__serialLine  = defaultSerialLine
    self.__serialSpeed = defaultSerialSpeed
    self.__lastBootMsg = defaultLastBootMsg
    self.__binPostFix = defaultBinPostFix
    self.serial_Client = serial.Serial(self.__serialLine, self.__serialSpeed, timeout=0)

  ##############################################################################
  #
  #  Method:
  #    get_targetip()
  #
  #  Description:
  #    Get actual Target-IP
  #
  #  Parameters:
  #    -
  #
  #  Return:
  #    self.__targetIP - Actual Target-IP
  #
  ##############################################################################

  def get_targetip(self) :
    return self.__targetIP

  ##############################################################################
  #
  #  Method:
  #    get_useNFS
  #
  #  Description:
  #    Get status-bit NFS have to be used or not
  #
  #  Parameters:
  #    -
  #
  #  Return:
  #    self.__useNFS - "0" when not used, "1" when used
  #
  ##############################################################################

  def get_useNFS(self) :
    return self.__useNFS

  ##############################################################################
  #
  #  Method:
  #    get_ftpUser
  #
  #  Description:
  #    Get Username for login issues
  #
  #  Parameters:
  #    -
  #
  #  Return:
  #    self.__ftpUser - Username given as a string
  #
  ##############################################################################

  def get_ftpUser(self) :
    return self.__ftpUser

  ##############################################################################
  #
  #  Method:
  #    get_ftpPasswd
  #
  #  Description:
  #    Get Password for login issues
  #
  #  Parameters:
  #    -
  #
  #  Return:
  #    self.__ftpPasswd - Password given as a string
  #
  ##############################################################################

  def get_ftpPasswd(self) :
    return self.__ftpPasswd

  ##############################################################################
  #
  #  Method:
  #    get_serialLine
  #
  #  Description:
  #    Get serial line
  #
  #  Parameters:
  #    -
  #
  #  Return:
  #    self.__serialLine - serial line given as a string
  #
  ##############################################################################

  def get_serialLine(self) :
    return self.__serialLine

  ##############################################################################
  #
  #  Method:
  #    get_serialSpeed
  #
  #  Description:
  #    Get serial speed
  #
  #  Parameters:
  #    -
  #
  #  Return:
  #    self.__serialSpeed - serial speed given as a string
  #
  ##############################################################################

  def get_serialSpeed(self) :
    return self.__serialSpeed

  ##############################################################################
  #
  #  Method:
  #    get_ftpPort
  #
  #  Description:
  #    Get ftp port
  #
  #  Parameters:
  #    -
  #
  #  Return:
  #    self.__ftpPort - ftp-port given as a string
  #
  ##############################################################################

  def get_ftpPort(self) :
    return self.__ftpPort

  ##############################################################################
  #
  #  Method:
  #    get_useTelnet
  #
  #  Description:
  #    Get status-bit Telnet have to be used or not
  #
  #  Parameters:
  #    -
  #
  #  Return:
  #    self.__useTelnet - "0" when not used, "1" when used
  #
  ##############################################################################

  def get_useTelnet(self) :
    return self.__useTelnet

  ##############################################################################
  #
  #  Method:
  #    get_telnetUser
  #
  #  Description:
  #    Get actual username for telnet login
  #
  #  Parameters:
  #    -
  #
  #  Return:
  #    self.__telnetUser - a username given as a string
  #
  ##############################################################################

  def get_telnetUser(self) :
    return self.__telnetUser

  ##############################################################################
  #
  #  Method:
  #    get_telnetPasswd
  #
  #  Description:
  #    Get actual passwrd for telnet login
  #
  #  Parameters:
  #    -
  #
  #  Return:
  #    self.__telnetPasswd - a password given as a string
  #
  ##############################################################################

  def get_telnetPasswd(self) :
    return self.__telnetPasswd

  ##############################################################################
  #
  #  Method:
  #    get_lastBootMsg()
  #
  #  Description:
  #    Get actual last boot message of target
  #
  #  Parameters:
  #    -
  #
  #  Return:
  #    self.__lastBootMsg - Actual last boot message
  #
  ##############################################################################

  def get_lastBootMsg(self) :
    return self.__lastBootMsg

  ##############################################################################
  #
  #  Method:
  #    get_binPostFix()
  #
  #  Description:
  #    Get postfix of test binary
  #
  #  Parameters:
  #    -
  #
  #  Return:
  #    self.__binPostFix - Postfix of test binary
  #
  ##############################################################################

  def get_binPostFix(self) :
    return self.__binPostFix

  ##############################################################################
  #
  #  Method:
  #    get_modules
  #
  #  Description:
  #    Get a list of all modules
  #
  #  Parameters:
  #    -
  # 
  #  Return:
  #    self.__moduletests - list of all modules
  #
  ##############################################################################

  def get_modules(self) :
    if self.__moduletests == None :
      # list of all module tests
      self.__moduletests = moduleList.getList()

    return self.__moduletests

  ##############################################################################
  #
  #  Method:
  #    get_module_names
  #
  #  Description:
  #    Get a list of all modules
  #
  #  Parameters:
  #    -
  # 
  #  Return:
  #    result - list of all module names
  #
  ##############################################################################

  def get_module_names(self) :
    result = []
    modules = str(self.get_modules())

    for module in self.get_modules() :
      result.append(module.getName())

    return result

  ##############################################################################
  #
  #  Method:
  #    get_testcases
  #
  #  Description:
  #    Get a list of all testcases in the module specified in moduleTestName
  #
  #  Parameters:
  #    moduleTestName - Moule-name from which all testcase-names needed
  #
  #  Return:
  #    testcases - list of all testcases in <moduleTestName>
  #
  ##############################################################################

  def get_testcases(self, moduleTestName) :
    testcases = []
    for this_module in self.get_modules() :
      # Get argument of self.get_modules() and cast to string
      string = str(this_module)
      # Look if this_module is the needed one defined in moduleTestName
      if moduleTestName in string :
        Module = this_module
        for i in Module.testprocedure :
          try :
            testcases.append(i.get_name() + '\n')
          except :
            pass
    return testcases
