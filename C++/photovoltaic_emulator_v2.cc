const int voltagePin = A0;   //voltage input from voltage divider
const int currentPin = A1;   //current sensor input
const float vcc = 5.0;
const int adcMax = 1023;
const float sens = 0.185;    //sensitivity for ACS712-5A

const float I_ph = 0.683;        //photogenerated current (A)
const float I_0 = 1e-10;         //diode reverse saturation current (A)
const float n = 1.3;             //ideality factor
const float T = 298.15;          //temperature in Kelvin (25°C)
const float q = 1.602e-19;       //elementary charge (C)
const float k = 1.38064852e-23;  //boltzmann constant (J/K)
const float R_s = 0.5;           //series resistance (ohm)
const float R_sh = 200.0;        //shunt resistance (ohm)


float readAverage(int pin, int samples = 100) {
  float sum = 0;
  for (int i = 0; i < samples; i++) {
    sum += analogRead(pin);
    delay(1);
  }
  return sum / samples;
}

float adcToVoltage(float adcValue) {
  return (adcValue / adcMax) * vcc;
}

float readCurrent() {
  float sensorVoltage = adcToVoltage(readAverage(currentPin));
  return (sensorVoltage - vcc / 2.0) / sens;  // Zero-centered at 2.5V
}

float readVoltage() {
  float rawVoltage = adcToVoltage(readAverage(voltagePin));
  float dividerRatio = 5.0;  // Adjust based on your resistor values
  return rawVoltage * dividerRatio;
}


void setup() {
  Serial.begin(9600);
}

void loop() {
  float V_oc = log(()/()) * ((k*)/())
  float V = readVoltage();     //terminal voltage
  float I_loss = readCurrent();  //measured current (e.g., losses)

  float diodeTerm = I_0 * (exp((q * (V + I_loss * R_s)) / (n * k * T)) - 1);
  float shuntTerm = (V + I_loss * R_s) / R_sh;
  float I_model = I_ph - diodeTerm - shuntTerm;

  float I_output = I_model - I_loss;

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
