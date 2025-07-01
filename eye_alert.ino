const int led = 2;
const int buzzer = 3;
unsigned long sayac = 0;
bool durum = false;
void setup() {
  pinMode(led, OUTPUT);
  pinMode(buzzer, OUTPUT);
  Serial.begin(9600);
}
void loop() {
  if (Serial.available()) {
    char veri = Serial.read();
    if (veri == '1') {
      durum = true;
    }
    else if (veri == '0') {
      durum = false;
      digitalWrite(led, LOW);
      digitalWrite(buzzer, LOW);
    }
  }
  if (durum) {
    unsigned long simdi = millis();
    if (simdi - sayac >= 500) {
      sayac = simdi;
      digitalWrite(led, !digitalRead(led));
      digitalWrite(buzzer, !digitalRead(buzzer));
    }
  }
}