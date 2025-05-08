#define voltageSensor A0
#define voltageModify 9

const float R1 = 100.0;
const float R2 = 1100.0;

void setup() {
  Serial.begin(9600);
  pinMode(voltageSensor, INPUT);
  pinMode(voltageModify, OUTPUT);
  Serial.println("Logical Voltage, Current, Measured voltage");
}

// givens
float G = 1000.0;
float I_sc = 0.683;
int P_mpp = 12;
float k = 1.380649 * pow(10, -23);
float kV = -2.93 * pow(10, -4);
float kI = 2.38 * pow(10, -4);
float K = 0.0018304961;
float NOCT = 320.15;
int N_p = 50;
int N_s = 49;
int n = 1;
float E_g = 1.602176634 * pow(10, -19);
float q = 1.602176634 * pow(10, -19);
float T_ref_kelvin = 298.15;

float V = 0.0;
float I = I_sc;

void loop(){
  float T_op = 1000.15;
  float Vt = (k * T_op)/q;
  Serial.print("Vt:");
  Serial.println(Vt);
  float I_ph = G*(I_sc + kI * (T_op - T_ref_kelvin));
  Serial.print("Iph:");
  Serial.println(I_ph);

  int V_oc = 25;
  float I_rs = (I_sc)/(exp((V_oc * q)/(n * k * T_op))-1);
  float I_s = I_rs * pow((T_op/T_ref_kelvin), 3) * exp(((-1*q*E_g)/(n*k)) * ((1/T_op)-(1/T_ref_kelvin)));

  for (int v = 0; v<=V_oc; v++) {
    float I_d = ((I_s * exp((V + (150000*I))/(n*Vt*N_s)))-I_s)*N_p);
    float I_sh = (V+(150000*I))/0.001;
    float I = (I_ph)*N_p - (I_d) - (I_sh);

    Serial.print(v);
    Serial.print(", ");
    Serial.print(I);
    Serial.print(", ");
  }
}
