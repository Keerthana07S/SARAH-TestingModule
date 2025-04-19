String inputString = "";
float G = 1000.0;
float T = 25.0;

float I_sc = 0.683;
float V_oc = 25.0;
float K_v = -0.07;
float K_i = 0.08;
int N_s = 49;
float R_s = 0.5;
float R_sh = 200.0;
float n = 1.3;
float q = 1.602e-19;
float k = 1.381e-23;
float T_ref = 298.15;
float E_g = 1.1;
float N_p = 1.0;

float V = 0.0;
float I = 0.0;

float calculate_vt(float T_kelvin) {
  return (k * T_kelvin) / q;
}

float calculate_irs(float T_kelvin) {
  float denom = exp((q * V_oc) / (n * k * T_kelvin)) - 1.0;
  return I_sc / denom;
}

float calculate_is(float I_rs, float T_kelvin) {
  float exponent = (-q * E_g / (n * k)) * ((1.0 / T_kelvin) - (1.0 / T_ref));
  return I_rs * pow(T_kelvin / T_ref, 3) * exp(exponent);
}

float calculate_iph(float G, float T_C) {
  return G * (I_sc + K_i * (T_C - (T_ref - 273.15)));
}

float calculate_id(float I_s, float V_t, float V, float I) {
  float exp_arg = (V + I * R_s) / (n * V_t * N_s);
  return I_s * (exp(exp_arg) - 1.0) * N_p;
}

float calculate_ish(float V, float I) {
  return (V + I * R_s) / R_sh;
}

float calculate_current(float V_input) {
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
