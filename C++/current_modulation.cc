int mosfetPin = 9; 
int voltageSensorPin = A0; 

float ISC = 0.683;  
float V_oc = 8.0;  
float beta = 8.0;

void setup() {
  pinMode(mosfetPin, OUTPUT); 
  Serial.begin(9600);
}

void loop() {
  float voltage = (analogRead(voltageSensorPin) / 1023.0) * V_oc; 

  float I_output = ISC * (1.0 - pow((voltage / V_oc), beta));
  I_output = constrain(I_output, 0.0, ISC); 

  int pwmValue = int((I_output / ISC) * 255.0);
  pwmValue = constrain(pwmValue, 0, 255);

  analogWrite(mosfetPin, pwmValue);

  Serial.print(voltage, 2); 
  Serial.print(",");
  Serial.print(I_output, 4); 
  Serial.print(",");
  Serial.println(pwmValue);

  delay(100);
}
