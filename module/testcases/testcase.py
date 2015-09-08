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
#* Module      : testcase.py
#*
#* Function    : Abstract class for testcases
#* Author      : Hubert
#* Date        : 2015-07-22
#*
#*
#* ----------------------------------------------------------------------------
#*
#******************************************************************************

import hedgehog

class Testcase(object) :
  def __init__(self) :
    pass

  ######################
  # Methods
  ######################

  ######################
  # Abstract Methods
  ######################

  ##############################################################################
  #
  #  Method: 
  #    process()
  #
  #  Description:
  #    Here your testcase should be implemented
  #
  #  Parameters:
  #    -
  #
  #  Return:
  #    0  - Testcase successful
  #   -1  - Testcase failed
  #
  ##############################################################################

  def process(self) :
    raise NotImplementedError("Please implement this method")
  
  ##############################################################################
  #
  #  Method: 
  #    get_name()
  #
  #  Description:
  #    Get the name of the testcase
  #
  #  Parameters:
  #    -
  #
  #  Return:
  #    self.__name - Name of the testcase
  #
  ##############################################################################

  def get_name(self) :
    raise NotImplementedError("Please implement this method")

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
    raise NotImplementedError("Please implement this method")

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
    raise NotImplementedError("Please implement this method")
