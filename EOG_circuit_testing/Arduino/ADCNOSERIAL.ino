
#include <ArduinoBLE.h>
BLEService EogService("1101");
BLEUnsignedIntCharacteristic outValueInt("2101", BLERead | BLENotify);

unsigned int valueHorizontal = 0;
unsigned int valueVertical = 0;
int minValueADC = 1024;
int maxValueADC = 0;

void setup() {
  //Serial.begin(115200);
  //while (!Serial);
  if (!BLE.begin()) {
    //Serial.println("Starting BLE failed!");
    while (1);
  }
  BLE.setLocalName("EOG Circuit");
  BLE.setAdvertisedService(EogService);
  EogService.addCharacteristic(outValueInt);
  BLE.addService(EogService);

  BLE.advertise();
  //Serial.println("Bluetooth device active, waiting for connections...");
}

void loop() {
  BLEDevice central = BLE.central();
  
  if (millis() >= 5000)  // starts after 5 seconds
  {
    if (central) {
      //Serial.print("Connected to central: ");
      //Serial.println(central.address());

      while (central.connected()) {
        //analogReadResolution(12);
        valueHorizontal = analogRead(0);
        valueVertical = analogRead(1);

        /*Serial.print(valueHorizontal);
        Serial.print(", ");
        Serial.println(valueVertical);*/
        outValueInt.writeValue(valueHorizontal + valueVertical*65536);
        delay(10); // Delay for > 60 fps, maximum that the game will run
      }
      /*Serial.print("Disconnected from central: ");
      Serial.println(central.address());*/
     }
  }
}
