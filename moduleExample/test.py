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
#* Module      : test.py
#*
#* Function    : Example-module
#* Author      : Hubert
#* Date        : 2015-07-22
#*
#*
#* ----------------------------------------------------------------------------
#*
#******************************************************************************

from module import moduletest
from module.testcases import apptestcase
import prepareini
import hedgehog

class Example(moduletest.ModuleTest) :
  def __init__(self) :
    self.testprocedure = [
                          prepareini.PrepareIni("Section",             # Name of section
                                                ["variable", "value"], # List of name=value pairs
                                                "/",                   # Path of .INI-File on target
                                                "myIniFile.INI"),      # Name of .INI-File
                          apptestcase.AppTestcase("Example_Testcase_No1",                 # Name of testcase
                                                  "moduleExample/ressources/exampletest", # Programm source path
                                                  "moduleExample/ressources/exampletest/hello_world", # Programm binary path
                                                  "/",                                    # Programm path on target
                                                  ["MY_FIRST_CALL"],                      # Arguments passed to testcase
                                                  None),                                  # Timeout (take default)
                          apptestcase.AppTestcase("Example_Testcase_No2",                 # Name of testcase
                                                  "moduleExample/ressources/exampletest", # Programm source path
                                                  "moduleExample/ressources/exampletest/hello_world", # Programm binary path
                                                  "/",                                    # Programm path on target
                                                  ["MY_SECOND_CALL"],                     # Arguments passed to testcase
                                                  None),                                  # Timeout (take default)
                          prepareini.PrepareIni(None, # None and ... 
                                                None, # ... None means the prepareini-class have to restore the original .INI-File
                                                "/",
                                                "myIniFile.INI")
                         ]

  def enter(self) :
    hedgehog.HedgeHog.instance().log("INFO", "Now i'm in module's enter-method")

  def leave(self) :
    hedgehog.HedgeHog.instance().log("INFO", "Now i'm in module' leave-method")
