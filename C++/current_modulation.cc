int mosfetPin = //mosfet pin #;  
int voltageSensorPin = A1; //virtual pin for now. ideally, an actual voltage sensor would be connected to this. 

float ISC = 0.683;  
float V_oc = 25.0;  

void setup() {
  pinMode(mosfetPin, OUTPUT); 

  Serial.begin(9600);
}

void loop() {
  float voltage = (analogRead(voltageSensorPin) / 1023.0) * V_oc; 

  float beta = 8.0;  
  float I_output = ISC * (1.0 - pow((voltage / V_oc), beta));
  float I_LOSS = (ISC - I_output);
  int pwmValue = int((I_LOSS / ISC) * 255.0); 

  pwmValue = constrain(pwmValue, 0, 255);

  analogWrite(mosfetPin, pwmValue);

  Serial.print("");
  Serial.print(voltage, 2); 
  Serial.print(",");
  Serial.print(I_output, 4); 
  Serial.print(",");
  Serial.println(pwmValue);

  delay(100); 
  
}
