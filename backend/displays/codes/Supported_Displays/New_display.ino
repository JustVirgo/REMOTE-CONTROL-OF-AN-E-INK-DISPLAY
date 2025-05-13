#ifdef __NEW_DISPLAY__ //Reaplce with your name in displays.json
#include "Display.h"
/*** Include your libraries ***/

/* EXAMPLE */
//#include <GxEPD2_BW.h>

/*** Initialization of the display ***/
void InitDisplay() {
  
}

/*** Edit this function for your specific display ***/
/* Data in buffer are stored according to specific type in displays.JSON and function you have to implement in display.py 
 * and add it in main.py to get_screen_picture fucntion */
 /* You have to setup the display correctly in the app, mainly the resolution */
void printToDisplay(uint8_t *buffer, uint32_t len) {
 
}
#endif