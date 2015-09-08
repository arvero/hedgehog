#******************************************************************************
#*
#* (C) 2015 by arvero GmbH
#*
#*  arvero GmbH
#*  Winchesterstraße 2
#*  D-35394 Gießen
#*
#* ----------------------------------------------------------------------------
#* Module      : readme.txt
#*
#* Function    : Explanation of hedgehog
#*
#* Author      : Hubert
#* Date        : 2015-07-22
#*
#*
#* ----------------------------------------------------------------------------
#*
#******************************************************************************

########################
# Topics
########################

1. Introduction

2. Teststart and output

3. Default parameters

4. Configuration-File

########################
# 1. Introduction
########################

This gives an overview about hedgehog and describes how to execute the existing
tests.

hedgehog can be used to test all kind of applications, API-functions or even
services. It consists of a list of module-tests, one module test for each
software component (e.g. MyApp, FTP-Server, Webserver, Serial-API, ...).
Each module-test holds a list of several testcases (e.g. testcase "login" for
module FTP-Server). The figure below illustrates an architectural overview by
means of a UML class diagramm.

+-------------------+               +-------------------+             +--------------------+
|     hedgehog      |               |    ModuleTest     |             |      Testcase      |
|-------------------|               |-------------------|             |--------------------|
| .                 |               | Enter <abstract>  |             | Get_Name()         |
| // Attributes     |1          0..*| Leave <abstract>  |1        0..*| Process <abstract> |
| .                 +---------------+ Process()         +-------------+                    |
| // Methods        |               |                   |             |                    |
| .                 |               |                   |             |                    |
| .                 |               |                   |             |                    |
|                   |               |                   |             |                    |
+-------------------+               +-------^-----------+             +----------^---------+
                                            |derived                             |derived
                               +------------+               +-------------------------+
                   +-----------+------+              +------+---------+      +--------+---------+
                   |  FTPModuleTest   |              | AppHelloTest   |      | FTPLoginTestcase |
                   |------------------|              |----------------|      |------------------|
                   |                  |              |                |      |                  |
                   |                  |              |                |      |                  |
                   |                  |              |                |      |                  |
                   |                  |              |                |      |                  |
                   |                  |              |                |      |                  |
                   |                  |              |                |      |                  |
                   +------------------+              +----------------+      +------------------+

#########################
# 2. Teststart and output
#########################

To execute all tests or particluar tests you can use the command "start.py"
script from command shell.

To start all tests type 

  # ./start.py -t <testee's ip address>

To start a particular moduletest type

  # ./start.py -t <testee's ip address> <module-test-name>

To get a list of all module test type

  # ./start.py -l

To start a particular test-case of a specific module type

  # ./start.py -t <testee's ip address> <module-test-name> <test-case-name>

To get a list of all test-cases of a specific module type

  # ./start.py -l <module-test-name>

Use ./start.py --help for more information

Currently the output will be shown on the shell but in further versions it is
also planned to put the output into a CSV or log file. Even the possibility to
show the output on shell will be still offered. The default output contains the
name of the testcase, a line to seperate each testcase and the result of your
testcase.

An output would look like:

INFO: INI-FILE PREPARED
INFO: ___________________
INFO: <YOUR-TESTCASE-NAME>
INFO: <YOUR CUSTOM OUTPUT>
INFO: <YOUR CUSTOM OUTPUT>
          .
          .
          .
INFO: Testcase: OK or Testcase: NOK

If some errors or warnings had occured an accordingly summary is given in the
end of the whole test execution. The summary looks like below:

ERROR: 1 errors occurred: 
ERROR: These testcases had failed: 

['FTPLogin-Testcase_No1', 'AppHelloTest_No1']

########################
# 3. Default Parameters
########################

The hedgehog-class has some default-attributes of communication and transfering
issues with ftp, telnet or nfs. The default values are set as follows:

    targetIP    = ''   # set-up by command line parameter or config-file
    useNFS      = 0
    ftpUser     = 'ftp'
    ftpPasswd   = 'ftp'
    ftpPort     = '21'
    serialLine  = '/dev/ttyS0'
    serialPort  = '19200'
    useTelnet   = 0
    telUser     = 'tel'
    telPass     = 'tel'
    lastBootMsg = 'Dummy_Last_Boot_Message'
    binPostFix  = ''

If it is required to modify one or more of these parameters please use the
according parameter from argument list of start.py.
If you want to, you also can configure hedgehog with a configuration-file.

########################
# 4. Configuration-File
########################

hedgehog can be configured with a configuration file. The name have to be
"hedgehog.config" and in the root directory of hedgehog. The syntax is as
follows:

    Name1=Value1
    Name2=Value2

Example:

    targetIP=192.168.2.69
    message=My Last Boot Message#

Possible names or rather options are:

  * target      - Targets IP address
  * ftpuser     - Login name for FTP
  * ftppass     - Login password for FTP
  * ftpport     - FTP port
  * sline       - Serial line to use
  * speed       - Serial baud rate
  * teluser     - Login name for telnet
  * telpass     - Login password for telnet
  * message     - Last boot message of target
  * control-log - Path to log file
  * binpostfix  - Postfix of test application(s)

NOTE: When an option is set in configuration file it will be overwritten when
      setting the same option via commandline argument
