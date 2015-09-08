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
#* Module      : moduleList.py
#*
#* Function    : Contains a list of all modules
#*
#* Author      : Stoidner
#* Date        : 2015-07-22
#*
#*
#* ----------------------------------------------------------------------------
#*
#******************************************************************************

##############################################################################
#
#  Method:
#    getList
#
#  Description:
#    Returns a list of all module tests. If you have created a new module
#    add it to the list AND add an according import statement at the end
#    of the file.
#
#  Return:
#    list of all modules
#
##############################################################################
def getList() :
  return [
    moduleExample.test.Example(),
  ]

# Import have to be here because of circular dependencies workaround
import moduleExample.test
