#******************************************************************************
#*
#* (C) 2015 by arvero GmbH
#*
#*  arvero GmbH
#*  Winchester Straße 2
#*  D-35394 Solms
#*
#* ----------------------------------------------------------------------------
#* Module      : Makefile
#*
#* Function    : Allows to build an example application
#* Author      : Hubert
#* Date        : 2015-07-22
#*
#*
#* ----------------------------------------------------------------------------
#*
#******************************************************************************

##############################
# application configuration
##############################

# name of the application's executable
APP_NAME=hello_world

# list of objects required for the application
APP_DEPENDENCIES=main.o

# list of libs required to link the application
APP_LIBS=

# Cross compiler prefix
CROSS_COMPILE=arm-linux-gnueabi-

CC=$(CROSS_COMPILE)gcc

###############
# Builder message
###############
hello:
	@echo ""
	@echo "--------------------------------------------------------------------------------"
	@echo " Makfile - Building $(APP_NAME) - application"
	@echo "--------------------------------------------------------------------------------"
	@echo ""

###############
# build
###############
build: hello 
	$(CC) -o $(APP_NAME) main.c

###############
# clean
###############
clean: 
	rm -rf $(APP_NAME) *.o
