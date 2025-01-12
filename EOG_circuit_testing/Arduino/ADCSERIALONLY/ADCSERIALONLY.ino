unsigned int valueHorizontal = 0;
unsigned int valueVertical = 0;
int minValueADC = 1024;
int maxValueADC = 0;

void setup() {
  Serial.begin(115200);
  while (!Serial);
}

void loop() {
  if (millis() >= 5000) { // starts after 5 seconds
      valueHorizontal = analogRead(0);
      valueVertical = analogRead(1);
      Serial.print(valueHorizontal);
      Serial.print(",");
      Serial.println(valueVertical);
      delay(2); // Delay for > 60 fps, maximum that the game will run
  }
}
