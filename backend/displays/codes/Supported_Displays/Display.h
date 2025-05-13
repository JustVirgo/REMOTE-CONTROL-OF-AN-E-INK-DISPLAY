#ifndef __DISPLAY_H__
#define __DISPLAY_H__

/*** Generated defines from the server ***/
#define DISPLAY_ID "2"
#define __LilyGO_TTGO_T5_4_7__
#define GET_DYNAMIC_SLEEP

/* Function for initializing the display */
void InitDisplay();

/* Function to copy the buffer to the display */ 
void printToDisplay(uint8_t *buffer, uint32_t len);

#endif