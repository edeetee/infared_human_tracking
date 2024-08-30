/***************************************************************************
  This is a library for the AMG88xx GridEYE 8x8 IR camera

  This sketch tries to read the pixels from the sensor

  Designed specifically to work with the Adafruit AMG88 breakout
  ----> http://www.adafruit.com/products/3538

  These sensors use I2C to communicate. The device's I2C address is 0x69

  Adafruit invests time and resources providing this open source code,
  please support Adafruit andopen-source hardware by purchasing products
  from Adafruit!

  Written by Dean Miller for Adafruit Industries.
  BSD license, all text above must be included in any redistribution
 ***************************************************************************/

#include <Wire.h>
#include <Adafruit_AMG88xx.h>

Adafruit_AMG88xx amg;

float pixels[AMG88xx_PIXEL_ARRAY_SIZE];

#define NUM_PIR 3
int pirPins[3] = {2, 3, 4};

void setup()
{
  Serial.begin(1000000);

  bool status;

  // default settings
  status = amg.begin();
  if (!status)
  {
    Serial.println("Could not find a valid AMG88xx sensor, check wiring!");
    while (1)
      ;
  }

  for (int i = 0; i < NUM_PIR; i++)
  {
    pinMode(pirPins[i], INPUT);
  }

  delay(100); // let sensor boot up
}

void loop()
{
  // wait for message from the host
  while (Serial.available() <= 0)
    ;

  // clear messages from the host
  while (Serial.available() > 0)
  {
    Serial.read();
  }

  // read all the pixels
  amg.readPixels(pixels);

  Serial.print("{");

  Serial.print("\"pir\": [");
  for (int i = 0; i < NUM_PIR; i++)
  {
    Serial.print(digitalRead(pirPins[i]));
    if (i < NUM_PIR - 1)
    {
      Serial.print(", ");
    }
  }
  Serial.print("],");

  Serial.print("\"ir\": [");
  for (int i = 1; i <= AMG88xx_PIXEL_ARRAY_SIZE; i++)
  {
    Serial.print(pixels[i - 1]);
    if (i < AMG88xx_PIXEL_ARRAY_SIZE)
    {
      Serial.print(", ");
    }
  }

  Serial.print("]");
  Serial.print("}");
  Serial.println();

  // delay a second
  //  delay(1000);
}
