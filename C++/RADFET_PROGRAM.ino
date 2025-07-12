int radSensorPin = A2;

float a = (0.79+0.89)/2;
float b = (0.0027+0.0028)/2;
float c = (0.92+0.9)/2;

void setup() {
  pinMode(radSensorPin, INPUT); 
  Serial.begin(9600);
}

void loop() {
  float V_t = (analogRead(radSensorPin) * (3.0/1023.0); 

  float D = (-(a)/(b*(V_t+a)) - 1)^(1/c);

  delay(100);
}
