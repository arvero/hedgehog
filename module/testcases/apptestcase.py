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
#* Module      : apptestcase.py
#*
#* Function    : This module contains a standard test case to test API 
#*               functionality.
#* Author      : Stoidner
#* Date        : 2015-07-22
#*
#*
#* ----------------------------------------------------------------------------
#*
#******************************************************************************
import os
import time
import hedgehog
from module.testcases import testcase

class AppTestcase(testcase.Testcase) :
  ##############################################################################
  #
  #  Method: 
  #    __init__()
  #
  #  Description:
  #    Creates an instance of the test case class.
  #
  #  Parameters:
  #    name              - name of the test case (e.g. "FTPLoginTest_No1")
  #    programSourcePath - path to root folder of the test program's sources
  #    programBinPath    - path to the binary executable which is built by
  #                        programSourcePath
  #    arg_list          - list of arguments that are given to program on start
  #    timeout           - timeout until some test result is printed on console
  #                        (optional, default is 10 seconds).
  #
  #  Return:
  #    -
  #
  ##############################################################################

  def __init__(self, name, programSourcePath, programBinPath, programFTPPath, arg_list, timeout=10) :
    self.programSourcePath = programSourcePath
    self.programBinPath = programBinPath
    self.programFTPPath = programFTPPath
    self.name = name
    self.timeout = timeout
    self.arg_list = arg_list

  ######################
  # Functions
  ######################

  ##############################################################################
  #
  #  Method: 
  #    get_name()
  #
  #  Description:
  #    Overwrite method form derived class.
  #
  #    See testcases.testcase.ModuleTest for more information.
  #
  #  Parameters:
  #    See testcases.testcase.ModuleTest for more information.
  #
  #  Return:
  #    See testcases.testcase.ModuleTest for more information.
  #
  ##############################################################################

  def get_name(self) :
    return self.name # return the name was passed to constructor

  ##############################################################################
  #
  #  Method: 
  #    enter()
  #
  #  Description:
  #    Overwrite method form derived class.
  #
  #    See testcases.testcase.ModuleTest for more information.
  #
  #  Parameters:
  #    See testcases.testcase.ModuleTest for more information.
  #
  #  Return:
  #    See testcases.testcase.ModuleTest for more information.
  #
  ##############################################################################

  def enter(self) :
    pass

  ##############################################################################
  #
  #  Method: 
  #    doControl()
  #
  #  Description:
  #    Overwrite method form derived class.
  #
  #    See testcases.testcase.ModuleTest for more information.
  #
  #  Parameters:
  #    See testcases.testcase.ModuleTest for more information.
  #
  #  Return:
  #    See testcases.testcase.ModuleTest for more information.
  #
  ##############################################################################

  def doControl(self, control_info) :
    pass

  ##############################################################################
  #
  #  Method: 
  #    process()
  #
  #  Description:
  #    Overwrite method form derived class.
  #
  #    See testcases.testcase.ModuleTest for more information.
  #
  #  Parameters:
  #    See testcases.testcase.ModuleTest for more information.
  #
  #  Return:
  #    See testcases.testcase.ModuleTest for more information.
  #
  ##############################################################################

  def process(self) :
    arguments = ""
    if self.arg_list != None :
      for item in self.arg_list :
        arguments += item
        arguments += " "

    result = 0 # assume success

    # building test program
    cwd = os.getcwd()
    try :
      hedgehog.HedgeHog.instance().log("INFO", "Performing Build of Test Program")
      os.chdir(self.programSourcePath)
      result = os.system("colormake build -B 1>/tmp/tf-build-output")
      if result != 0 :
        hedgehog.HedgeHog.instance().log("ERROR", "Build has failed, see error(s) below:");
        hedgehog.HedgeHog.instance().log("ERROR", "================================================================================")
        os.system("cat /tmp/tf-build-output")
        os.system("rm /tmp/tf-build-output")
        hedgehog.HedgeHog.instance().log("ERROR", "================================================================================")
        return -1
    finally :
      os.chdir(cwd)

    # deploying test program
    hedgehog.HedgeHog.instance().log("INFO", "Deploying Test Program")
    hedgehog.HedgeHog.instance().fileSend(self.programBinPath, self.programFTPPath + "apptest" + hedgehog.HedgeHog.instance().get_binPostFix())

    # clean test program
    cwd = os.getcwd()
    try :
      os.chdir(self.programSourcePath)
      result = os.system("make clean 1>/dev/null")
      if result != 0 :
        hedgehog.HedgeHog.instance().log("WARNING", "Clean has failed")
    finally :
      os.chdir(cwd)

    # clearing all old lines received from remote shell
    hedgehog.HedgeHog.instance().remoteShellClearRecvBuffer()

    # starting test program
    hedgehog.HedgeHog.instance().log("INFO", "Starting Test Program")
    hedgehog.HedgeHog.instance().remoteShellSend(self.programFTPPath + "apptest" + hedgehog.HedgeHog.instance().get_binPostFix() + " " + arguments + "\r\n")

    # waiting for test program's start message
    line = hedgehog.HedgeHog.instance().remoteShellReceive(".*INFO: test was started", self.timeout)
    if line == None :
      hedgehog.HedgeHog.instance().log("ERROR", "Error starting program! Assumedly program could not be transfered or started, or it does not output start message \"INFO: test was started\"!")
      return -1

    # observing console output
    while True :
      # the expected output is:

      # [INFO|WARNING|ERROR]: [human readable result message]
      # Examples:
      #   INFO: Function foo() was successful
      #   ERROR: Function bar() returned negative value
      line = hedgehog.HedgeHog.instance().remoteShellReceive("WARNING|ERROR|INFO|CONTROL: .*", self.timeout)
      if line == None :
        hedgehog.HedgeHog.instance().log("ERROR", "Missing expected output of test pogram. Program may still be running, so next test could also fail!")
        result = -1
        break

      lineItems = line.split(":")
      lineItems[0] = lineItems[0].rstrip(' ')
      lineItems[1] = lineItems[1].lstrip(' ')

      if "CONTROL" in lineItems[0] :
        if self.doControl(lineItems[1]) == -1 :
          result = -1
      elif "ERROR" in lineItems[0] :
        result = -1

      # TODO: Handle "INFO: waiting for service access" message!
      if "INFO: test was finished" in line :
        time.sleep(1) # give program some time to terminate
        break # test is completed
      else :
        hedgehog.HedgeHog.instance().log(lineItems[0], lineItems[1])

    return result

  ##############################################################################
  #
  #  Method: 
  #    leave()
  #
  #  Description:
  #    Overwrite method form derived class.
  #
  #    See testcases.testcase.ModuleTest for more information.
  #
  #  Parameters:
  #    See testcases.testcase.ModuleTest for more information.
  #
  #  Return:
  #    See testcases.testcase.ModuleTest for more information.
  #
  ##############################################################################

  def leave(self) :
    # Need to delete testfile on server
    hedgehog.HedgeHog.instance().remoteShellSend("del /apptest"  + hedgehog.HedgeHog.instance().get_binPostFix() + "\r\n")
    hedgehog.HedgeHog.instance().remoteShellSend("rm /apptest" + hedgehog.HedgeHog.instance().get_binPostFix() + "\r\n")
