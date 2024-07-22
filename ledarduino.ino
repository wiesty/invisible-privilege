int green = 13;
int red = 12;

void setup() {
    pinMode(green, OUTPUT);
    pinMode(red, OUTPUT);
    Serial.begin(9600);
    digitalWrite(green, HIGH);
    digitalWrite(red, HIGH);
}

void loop() {
    if (Serial.available() > 0) {
        char command = Serial.read();

        if (command == 'R') {
            digitalWrite(green, HIGH);
            digitalWrite(red, LOW);
        } else if (command == 'G') {
            digitalWrite(green, LOW);
            digitalWrite(red, HIGH);
        } else if (command == 'O') {
          digitalWrite(green, HIGH);
          digitalWrite(red, HIGH);
        }
    }
}
