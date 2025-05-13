
#ifdef __LilyGO_TTGO_T5_4_7__
#include "Display.h"
#include "epd_driver.h" 
/**
 * @note      Arduino Setting
 *            Tools ->
 * Board:"ESP32S3 Dev Module"
 * USB CDC On Boot:"Enable"
 * USB DFU On Boot:"Disable"
 * Flash Size : "16MB(128Mb)"
 * Flash Mode"QIO 80MHz
 * Partition Scheme:"16M Flash(3M APP/9.9MB FATFS)"
 * PSRAM:"OPI PSRAM"
 * Upload Mode:"UART0/Hardware CDC"
 * USB Mode:"Hardware CDC and JTAG"
 *
 */

void InitDisplay() {
  epd_init();
}

/*** Edit this function for your specific display ***/
/* Data in buffer are stored according to specific type in displays.JSON and function you have to implement in display.py 
 * and add it in main.py to get_screen_picture fucntion */
/* You have to setup the display correctly in the app, mainly the resolution */
void printToDisplay(uint8_t *buffer, uint32_t len) {

  epd_poweron();
  epd_clear();
  volatile uint32_t t1 = millis();
  epd_draw_grayscale_image(epd_full_screen(), buffer);
  volatile uint32_t t2 = millis();
  Serial.printf("EPD draw took %dms.\r\n", t2 - t1);
  epd_poweroff();
}
#endif