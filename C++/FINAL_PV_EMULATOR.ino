//author: keerthana srinivasan
//date of completion: 6/1/2025
//description: emulator that demonstrates classive photovoltaic characteristics through IV curve generation. 

const int voltagePin = A0;  //voltage output (V-out) from voltage divider
const int currentPin = A1;  //current output (I-loss)
const float vcc = 5.0; //vcc
const int adcMax = 1023; //for voltage sensor processing
const float sens = 0.185;  //noice 

//givens
const float I_ph = 0.683;
const float I_0 = 1e-10;      
const float n = 1.3;            
const float T = 298.15;  //in the event a thermistor is available, the function to obtain temperature  could also be applicable  
const float q = 1.602e-19;       
const float k = 1.38064852e-23; 
const float R_s = 0.5;        
const float R_sh = 200.0;       


//average the readings from the voltage and current sensors to avoid extreme noise
float readAverage(int pin, int samples = 100) {
  float sum = 0;
  for (int i = 0; i < samples; i++) {
    sum += analogRead(pin);
    delay(1);
  }
  return sum / samples;
}

//take sensor voltage and calculate regular voltage
float adcToVoltage(float adcValue) {
  return (adcValue / adcMax) * vcc;
}

float readCurrent() {
  float sensorVoltage = adcToVoltage(readAverage(currentPin));
  return (sensorVoltage - vcc / 2.0) / sens;  //zero-centered at 2.5V
}

float readVoltage() {
  float rawVoltage = adcToVoltage(readAverage(voltagePin));
  float dividerRatio = 5.0;  //adjust based on your resistor values
  return rawVoltage * dividerRatio;
}


void setup() {
  Serial.begin(9600);
}

void loop() {
  float V = readVoltage();   //current voltage
  float I_loss = readCurrent();  //i-loss 
  
  float diodeTerm = I_0 * (exp((q * (V + I_loss * R_s)) / (n * k * T)) - 1); //i_ds
  float shuntTerm = (V + I_loss * R_s) / R_sh; //i_sh
  float I_model = I_ph - diodeTerm - shuntTerm; //general i based on previous values

  float I_output = I_model - I_loss; //i_output

  Serial.print("Voltage (V): ");
  Serial.println(V, 2);
  Serial.print("Measured Current (A): ");
  Serial.println(I_loss, 3);
  Serial.print("Model Current (A): ");
  Serial.println(I_model, 3);
  Serial.print("Output Current (A): ");
  Serial.println(I_output, 3);
  Serial.println("-----");

  delay(1000);
}
