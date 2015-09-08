/******************************************************************************
#*
#* (C) 2015 by arvero GmbH
#*
#*  arvero GmbH
#*  Winchesterstraße 2
#*  D-35394 Gießen
#*
#* ----------------------------------------------------------------------------
#* Module      : main.c
#*
#* Function    : Example testcase application
#*               
#* Author      : Hubert
#* Date        : 2015-07-22
#*
#*
#* ----------------------------------------------------------------------------
#*
#******************************************************************************/

#include <stdio.h>

int main(int argc, char *argv[])
{
  /*
   *  This output is needed so that hedgehog get to know that testcase was
   *  successfully started
   */
  printf("INFO: test was started\n");

  printf("Hello World\n");

  if(argv[1] != NULL)
    printf("%s\n", argv[1]);

  /*
   *  This output is needed so that hedgehog get to know that testcase was
   *  finished
   */
  printf("INFO: test was finished\n");

  return 0;
}
