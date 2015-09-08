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
#* Module      : moduletest.py
#*
#* Function    : An abstract class of a module
#* Author      : Hubert
#* Date        : 2015-07-22
#*
#*
#* ----------------------------------------------------------------------------
#*
#******************************************************************************

import time
import testcases.testcase
import hedgehog

prepare_was_before = 0

class ModuleTest :
  def __init__(self) :
    self.testprocedure = []

  ##############
  # Methods
  ##############

  ##############################################################################
  #
  #  Method:
  #    process()
  #
  #  Description:
  #    Iterates through all parameters in "self.testcases" and call their
  #    process()-method. Furthermore keep count of errors.
  #
  #  Parameters:
  #    testcaseName - An optional testcase-name given as a string that defines 
  #                   the testcase which have to be executed
  #
  #  Return:
  #    -
  #
  ##############################################################################

  def process(self, testcaseName) :
    global prepare_was_before

    for this_testcase in self.testprocedure :
      if testcaseName == None or testcaseName == "" :

        # We don't want to execute a specific testcase, just execute all in that module

        if (isinstance(this_testcase, testcases.testcase.Testcase)) :
          # When its an instance, we need the name
          hedgehog.HedgeHog.instance().log("INFO", "___________________")
          hedgehog.HedgeHog.instance().log("INFO", "")
          hedgehog.HedgeHog.instance().log("INFO", this_testcase.get_name())
          if prepare_was_before == 1 :
            # Check if an .INI-File was changed by prepareini-class, so that we have to
            # reboot the target to accept the new configurations
            self.makeReboot()

        else :
          # Otherwise its not a testcase but a call to prepare an .INI-File
          hedgehog.HedgeHog.instance().log("INFO", "Preparing .INI-File")
          prepare_was_before = 1

        # Save that testcase in a variable and check if its an instance of testcase
        # if so, call the enter-method of that testcase, which have to be implemented
        testcase = this_testcase
        if (isinstance(testcase, testcases.testcase.Testcase)) :
          try :
            testcase.enter()
          except Exception,e :
            raise NotImplementedError("Please implement \"enter()\" method in test-case \"" + this_testcase.get_name() + "\"")

        # Finally call the process method to start the testcase
        result = testcase.process()

      else :

        # Here we want to execute a specific testcase

        if (isinstance(this_testcase, testcases.testcase.Testcase)) :
          # Get name of testcase to check if its the needed one
          currentTestcaseName = str(this_testcase.get_name())
          if testcaseName in currentTestcaseName :
            # Found the needed testcase
            if prepare_was_before == 1 :
              # Check if an .INI-File was changed by prepareini-class, so that
              # we have to reboot the target to accept the new configurations
              self.makeReboot()

            testcase = this_testcase
            hedgehog.HedgeHog.instance().log("INFO", "___________________")
            hedgehog.HedgeHog.instance().log("INFO", currentTestcaseName)
            try :
              testcase.enter()
            except Exception,e :
              raise NotImplementedError("Please implement \"enter()\" method in test-case \"" + this_testcase.get_name() + "\"")

            # Finally call the process method to start the testcase
            result = testcase.process()

          else :
            result = 99

        else :
          # Otherwise its not a testcase but a call to prepare an .INI-File
          hedgehog.HedgeHog.instance().log("INFO", "Preparing .INI-File")
          prepare_was_before = 1
          # Call prepareini process-method
          testcase = this_testcase
          result = testcase.process()

      if result == 0 :
        hedgehog.HedgeHog.instance().log("INFO", "Testcase: OK")
      elif result == 1 :
        hedgehog.HedgeHog.instance().log("INFO", "INI-FILE PREPARED")
      elif result == 2 :
        hedgehog.HedgeHog.instance().log("INFO", "INI-FILE RESTORED")
        # When we restore an .INI-File we have to reboot the target to accept
        # new configuration
        self.makeReboot()
      elif result == 99 :
        # Here we come when we want to find a specific testcase, but its not the current one
        # so we have to search further
        pass
      elif result == -1 :
        hedgehog.HedgeHog.instance().log("ERROR", "Testcase: NOK")
        hedgehog.HedgeHog.instance().add_error(testcase.get_name())
      else :
        hedgehog.HedgeHog.instance().log("WARNING", "UNACCEPTABLE RETURN-CODE FROM :" + str(testcase))

      # After process finished we call the leave method (when its a testcase and not prepareini)
      if (isinstance(this_testcase, testcases.testcase.Testcase)) :
        try :
          this_testcase.leave()
        except Exception,e :
          raise NotImplementedError("Please implement \"leave()\" method in test-case \"" + this_testcase.get_name() + "\"")

    # END OF FOOR-LOOP

  ##############################################################################
  #
  #  Method:
  #    getName()
  #
  #  Description:
  #    Returns the name of the module
  #
  #  Parameters:
  #    -
  #
  #  Return:
  #    moduleName - Name of the module
  #
  ##############################################################################

  def getName(self) :
    moduleName = str(self)
    # Split to second "."-character
    moduleName = moduleName.split(".",2)[2]
    # Split to first " "-character 
    moduleName = moduleName.split(" ",1)[0]
    return moduleName

  ##############################################################################
  #
  #  Method:
  #    makeReboot()
  #
  #  Description:
  #    Send a reboot-command to target and waits until its finished with
  #    booting
  #
  #  Parameters:
  #    -
  #
  #  Return:
  #    -
  #
  ##############################################################################

  def makeReboot(self) :
    global prepare_was_before
    # TODO: Check if a reboot is needed to accept new INI-File configuration
    hedgehog.HedgeHog.instance().log("INFO", "Rebooting testee to accept new INI-File configuration")
    hedgehog.HedgeHog.instance().remoteShellSend("\nreboot\n")
    # Wait and catch last boot message
    line = hedgehog.HedgeHog.instance().remoteShellReceive(hedgehog.HedgeHog.instance().get_lastBootMsg(), 120)
    if line == None :
      hedgehog.HedgeHog.instance().log("ERROR", "Target does not answer after reboot! Subsequent test(s) could fail!")

    # After reboot it could be that we have to press enter to activate the console
    time.sleep(1)
    hedgehog.HedgeHog.instance().remoteShellSend("\n")
    # Since we rebooted and accepted new configuration we can reset that flag
    prepare_was_before = 0

  ######################
  # Abstract Functions
  ######################
  def enter(self) :
    raise NotImplementedError("Please implement this method")

  def leave(self) :
    self.makeReboot()
