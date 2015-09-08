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
#* Module      : prepareini.py
#*
#* Function    : Prepare and restore .INI-File before and after testcase
#*               scenario
#* Author      : Hubert
#* Date        : 2015-07-22
#*
#*
#* ----------------------------------------------------------------------------
#*
#******************************************************************************

import hedgehog
import os.path
import shutil
import tempfile

# Get a random name for .INI-File from target
random = tempfile.NamedTemporaryFile(prefix="MyINIFile-", delete=False)
port_change = 0

class PrepareIni :
  ##############################################################################
  #
  #  Method: 
  #    __init__()
  #
  #  Description:
  #    Creates an instance of the prepareini class.
  #
  #  Parameters:
  #    section        - Sectionname which have to be set
  #    name_val_array - Name value pairs of the option to be set
  #    inifilePath    - Path of .INI-File on target
  #    inifileName    - Name of .INI-File on target
  #
  #  Return:
  #    -
  #
  ##############################################################################

  def __init__(self, section, name_val_array, inifilePath, inifileName) :
    # Array is like ["<name>", "<value>", "<name>", "<value>", .... ]
    self.section = section
    self.name_val_array = name_val_array
    self.inifilePath = inifilePath
    self.inifileName = inifileName

  ##############
  # Methods
  ##############

  ##############################################################################
  #
  #  Method: 
  #   remove_temp_files()
  #
  #  Description:
  #    Remove temporary .INI-Files
  #
  #  Parameters:
  #    -
  #
  #  Return:
  #    -
  #
  ##############################################################################

  @staticmethod
  def remove_temp_files() :
    # Removing old .INI-File in /temp/
    os.remove(random.name)

  ##############################################################################
  #
  #  Method: 
  #   backup_inifile()
  #
  #  Description:
  #    Get the not touched .INI-File from target to reconstruct old state after 
  #    done all testcases
  #
  #  Parameters:
  #    -
  #
  #  Return:
  #    -
  #
  ##############################################################################

  def backup_inifile(self) :
    # Get actual .INI-File from Server if there is no .INI-File in actual directory
    hedgehog.HedgeHog.instance().fileRetrieve(self.inifilePath + self.inifileName, random.name)
    # Make a copy to the actual directory
    shutil.copy(random.name, self.inifileName)

  ##############################################################################
  #
  #  Method: 
  #    restore_inifile()
  #
  #  Description:
  #    Restore old state of .INI-File on target and clear local temporary
  #    .INI-File. Furthermore set username and password to default
  #
  #  Parameters:
  #    -
  #
  #  Return:
  #    -
  #
  ##############################################################################

  def restore_inifile(self) :
    global port_change

    if port_change != 0 :
      hedgehog.HedgeHog.instance().set_ftpPort(str(port_change))
    elif port_change == 0 :
      hedgehog.HedgeHog.instance().set_ftpPort('21')
    # Putting old .INI-File back on Server
    hedgehog.HedgeHog.instance().fileSend(random.name, self.inifilePath + self.inifileName)
    # Erase contents of local .INI-File
    open(self.inifileName, 'w').close()
    # Set hedgehog-attributes to default
    hedgehog.HedgeHog.instance().restoreFromDefaultValues()
    self.remove_temp_files()
    # Removing used .INI-File in actual path
    os.remove(self.inifileName)

  ##############################################################################
  #
  #  Method: 
  #    process()
  #
  #  Description:
  #    Write .INI-parameters in .INI-File that will be uses in testcases
  #    and put it on Target.
  #    Handling .INI-File backup before and restore after testcase-scenario.
  #
  #  Parameters:
  #    -
  #
  #  Return:
  #    1 - .INI-File was successful prepared
  #    2 - .INI-File was successful restored
  #
  ##############################################################################

  def process(self) :
    global port_change
    # Want to use FTP
    hedgehog.HedgeHog.instance().set_useNFS = 0

    if not os.path.isfile(self.inifileName) :
      self.backup_inifile()

    if self.section == None and self.name_val_array == None :
      self.restore_inifile()
      return 2

    else :
      for item in range(0, len(self.name_val_array), 2) :
        # Write Parameters into .INI-File
        hedgehog.HedgeHog.instance().set_iniString(self.inifileName, self.section, self.name_val_array[item], self.name_val_array[item + 1])

        # In case of ftp and telnet we need to change user and password in hedgehog for login issues
        if self.section == '[FTP]' or '[TELNET]' :
          if self.name_val_array[item] == 'user0' or self.name_val_array[item] == 'user1' :
            # Set new value for ftpUser
            newUsername = self.name_val_array[item + 1]

          elif self.name_val_array[item] == 'password0' or self.name_val_array[item] == 'password1' :
            # Set new value for ftpPasswd
            newPassword = self.name_val_array[item + 1]
          else :
            newUsername = 'ftp'
            newPassword = 'ftp'

      # Put .INI-File to target for running testcases
      hedgehog.HedgeHog.instance().fileSend(self.inifileName, self.inifilePath + self.inifileName)

      hedgehog.HedgeHog.instance().set_ftpUser(newUsername)
      hedgehog.HedgeHog.instance().set_ftpPasswd(newPassword)

      if len(hedgehog.HedgeHog.instance().get_ftpUser()) == 0 or len(hedgehog.HedgeHog.instance().get_ftpPasswd()) == 0 :
        hedgehog.HedgeHog.instance().set_ftpUser('ftp')
        hedgehog.HedgeHog.instance().set_ftpPasswd('ftp')

      if self.name_val_array[0] == 'user1' and self.name_val_array[1] == 'ftp' and len(self.name_val_array[3]) > 0 :
        hedgehog.HedgeHog.instance().set_ftpUser('ftp')
        hedgehog.HedgeHog.instance().set_ftpPasswd('ftp')

      if self.name_val_array[0] == 'cmdport' and self.name_val_array[1] != 21 :
        port_change = self.name_val_array[1]
      elif self.name_val_array[0] == 'cmdport' and self.name_val_array[1] == 21 :
        port_change = 0
    return 1
