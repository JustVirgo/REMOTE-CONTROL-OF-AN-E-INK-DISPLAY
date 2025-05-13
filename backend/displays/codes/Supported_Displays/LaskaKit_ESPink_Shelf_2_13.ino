#ifdef __LaskaKit_ESPink_Shelf_2_13__
#include "Display.h"
#include <GxEPD2_BW.h>

GxEPD2_BW<GxEPD2_213_B74, GxEPD2_213_B74::HEIGHT> display(GxEPD2_213_B74(/*CS=5*/ SS, /*DC=*/ 17, /*RST=*/ 16, /*BUSY=*/ 4));     // ESPink-Shelf-213 GDEM0213B74 -> 2.13" 122x250, SSD1680
//GxEPD2_BW<GxEPD2_213_GDEY0213B74, GxEPD2_213_GDEY0213B74::HEIGHT> display(GxEPD2_213_GDEY0213B74(/*CS=5*/ SS, /*DC=*/ 17, /*RST=*/ 16, /*BUSY=*/ 4)); // GDEY0213B74 128x250, SSD1680, (FPC-A002 20.04.08)

void InitDisplay() {
  // turn on power to display`  
  pinMode(2, OUTPUT); 
  digitalWrite(2, HIGH);   // turn on the ePaper
  delay(1000);   
  
  display.init(); // ePaper init
  display.setRotation(0);
  display.setFullWindow();
  display.firstPage();
  display.fillScreen(GxEPD_WHITE); // set the background to white (fill the buffer with value for white)
  display.display();
  
}

/*** Edit this function for your specific display ***/
/* Data in buffer are stored according to specific type in displays.JSON and function you have to implement in display.py 
 * and add it in main.py to get_screen_picture fucntion */
void printToDisplay(uint8_t *buffer, uint32_t len) {
  //void drawImage(const uint8_t bitmap[], int16_t x, int16_t y, int16_t w, int16_t h, bool invert = false, bool mirror_y = false, bool pgm = false)
  display.drawImage(buffer, 0, 0, 128, 250);
}
#endif