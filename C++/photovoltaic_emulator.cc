#define tempPin A1
#define voltageSensor A0
#define voltageModify 9
const float R1 = 10000.0;
const float R2 = 6800.0; 

void setup() {
  Serial.begin(9600);
  pinMode(tempPin, INPUT);
  pinMode(voltageSensor, INPUT);
  pinMode(voltageModify, OUTPUT);
  String input = "Hello";
}


void setup() {
  Serial.begin(9600);
  pinMode(tempPin, INPUT);
  pinMode(voltageSensor, INPUT);
  pinMode(voltageModify, OUTPUT);
}

float G = 1000.0; // will be adding a function soon to obtain this from a radfet

float obtain_temp() {
  int reading = analogRead(tempPin);
  float voltage = reading * (5000/1024.0);
  float T_celsius = (voltage-500)/10;
  float T_kelvin = T_celsius + 273.15;
  return T_kelvin;
}

float I_sc = 0.683;
int P_mpp = 12;
float k = 1.38064852e-23;
float K_v = -0.08;
float K_i = 0.065;
float K = 0.5;
int NOCT = 47;
int N_p = 50;
int N_s = 49;
float R_s = 0.5;
float R_sh = 200.0;
float n = 1.3;
float q = 1.602e-19;
float T_ref_kelvin = 298.15;
float E_g = 1.1;
float N_p = 1.0;

float V = 0.0;
float I = 0.0;

float calculate_vt(float T_kelvin) {
  float V_t = (k * T_kelvin) / q;
  return V_t;
}

float calculate_voc(float I_ph, float I_s, float V_t){
  float V_oc = std::log(I_ph/I_s) * V_t;
  return V_oc;
}

float calculate_irs(float T_kelvin, float I_sc, float q, float n, float K) {
  float denom = exp((q * V_oc) / (n * k * T_kelvin)) - 1.0;
  float I_rs = I_sc / denom;
  return I_rs;
}

float calculate_is(float I_rs, float T_kelvin) {
  float exponent = (-q * E_g / (n * k)) * ((1.0 / T_kelvin) - (1.0 / T_ref));
  return I_rs * pow(T_kelvin / T_ref, 3) * exp(exponent);
}

float calculate_iph(float G, float T_kelvin, float T_ref_kelvin, float I_sc, float K_i) {
  float I_ph = G * (I_sc + K_i*(T_kelvin - T_ref_kelvin));
  return I_ph
}

float calculate_id(float I_s, float V_t, float V, float I) {
  float exp_arg = (V + I * R_s) / (n * V_t * N_s);
  float I_d = I_s * (exp(exp_arg) - 1.0) * N_p;
  return I_d;
}

float calculate_ish(float V, float I) {
  float I_sh = (V + I * R_s) / R_sh;
  return I_sh;
}

float T_op = obtain_temp();
float V_t = calculate_vt(T_op);
float I_ph = calculate_iph(G, T_op, T_ref_kelvin, I_sc,  K_i);
float V_oc = 25.0;
float I_rs = calculate_irs(I_sc, V_oc, q, n, k, T_op);
float I_s = calculate_is(I_rs, T_op);
float V_oc = calculate_voc(I_ph, I_s, V_t);

float calculate_current(float I_ph, float N_p, float I_d, float I_sh) {
  float I = I_ph * N_p - I_d - I_sh;
  return I;
}

float I = 0.0;

void loop() {
  if (Serial.available()) {
    String input = Serial.readStringUntil('\n');

    if (input == "Hello") {
      float T_op = obtain_temp();
      float V_t = calculate_vt(T_op);
      float I_ph = calculate_iph(G, T_op, I_sc, K_i);

      float V_oc_guess = 25.0; // we set an initial value for V_oc until we can calculate the actual value
      float I_rs = calculate_irs(I_sc, V_oc_guess, q, n, k, T_op);
      float I_s = calculate_is(I_rs, T_op);
      float V_oc = calculate_voc(I_ph, I_s, V_t); // we calculate the actual value for V_oc

      Serial.println("Voltage (V), Current (A), Battery (V)");
      float I = I_sc; // the current always initially starts on I_sc
      
      for (int v = 0; v <= V_oc; v += 0.5) {
        float I_d = calculate_id(I_s, V_t, v, I);
        float I_sh = calculate_ish(v, I);
        I = calculate_current(I_ph, I_d, I_sh); // we calculate the new current

        Serial.print(v);
        Serial.print(", ");
        Serial.print(I);
        Serial.print(", ");

        analogWrite(voltageModify, 255);
        int sensorValue = analogRead(voltageSensor);
        float voltageAtPin = sensorValue * (5.0 / 1023.0); // voltage at A0
        float batteryVoltage = voltageAtPin * ((R1 + R2) / R2); // undo the voltage divider
        Serial.print(batteryVoltage);
        Serial.println();
        delay(1000);
      }
    }
  }
}
