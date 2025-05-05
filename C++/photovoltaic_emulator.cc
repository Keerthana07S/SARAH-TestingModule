#define tempPin A1;
#define voltageSensor A0;
#define voltageModify 9;

void setup() {
  Serial.begin(9600);
  pinMode(tempPin, INPUT);
  pinMode(voltageSensor, INPUT);
  pinMode(voltageModify, OUTPUT);
}

float G = 1000.0; // will be adding a function soon to obtain this from a radfet

float obtain_temp {
  int reading = analogRead(tempPin);
  float voltage = reading * (5000/1024.0);
  float T_celsius = (voltage-500)/10;
  float T_kelvin = T_celsius + 273.15;
  return T_kelvin;
}

float I_sc = 0.683;
int P_mpp = 12;
float K_v = -0.08;
float K_i = 0.065;
float K = 0.5;
int NOCT = 47;
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

calculate_vt(float T_kelvin) {
  float V_t = (k * T_kelvin) / q;
  return V_t
}

calculate_irs(float T_kelvin, float I_sc, float q, float n, float K) {
  float denom = exp((q * V_oc) / (n * k * T_kelvin)) - 1.0;
  float I_rs = I_sc / denom;
  return I_rs;
}

calculate_is(float I_rs, float T_kelvin) {
  float exponent = (-q * E_g / (n * k)) * ((1.0 / T_kelvin) - (1.0 / T_ref));
  return I_rs * pow(T_kelvin / T_ref, 3) * exp(exponent);
}

calculate_iph(float G, float T_kelvin, float T_ref_kelvin) {
  float I_ph = G * (I_sc + K_i*(T_kelvin - T_ref_kelvin));
  return I_ph
}

calculate_id(float I_s, float V_t, float V, float I) {
  float exp_arg = (V + I * R_s) / (n * V_t * N_s);
  return I_s * (exp(exp_arg) - 1.0) * N_p;
}

calculate_ish(float V, float I) {
  return (V + I * R_s) / R_sh;
}

calculate_current(float V_input) {
  float T_kelvin = T + 273.15;
  float V_t = calculate_vt(T_kelvin);
  float I_rs = calculate_irs(T_kelvin);
  float I_s = calculate_is(I_rs, T_kelvin);
  float I_ph = calculate_iph(G, T);

  float I_est = I_ph;
  for (int i = 0; i < 10; i++) {
    float I_d = calculate_id(I_s, V_t, V_input, I_est);
    float I_sh = calculate_ish(V_input, I_est);
    float I_new = I_ph * N_p - I_d - I_sh;
    if (abs(I_new - I_est) < 1e-5) break;
    I_est = I_new;
  }
  return I_est;
}

void setup() {
  Serial.begin(9600);
}

void loop() {
  if (Serial.available()) {
    inputString = Serial.readStringUntil('\n');
    int commaIndex = inputString.indexOf(',');
    if (commaIndex > 0) {
      String gString = inputString.substring(0, commaIndex);
      String tString = inputString.substring(commaIndex + 1);
      G = gString.toFloat();
      T = tString.toFloat();
    }
  }

  V = analogRead(A0) * (5.0 / 1023.0);
  I = calculate_current(V);

  Serial.print(V, 3);
  Serial.print(",");
  Serial.println(I, 3);

  delay(200);
}
