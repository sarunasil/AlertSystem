#define BUZZER 12
#define TIME_DELAY 150
#define LED 13

void ringer_setup(){
    pinMode(BUZZER, OUTPUT);
    Serial.println("Buzzer setup done.");
}

void ring(){
    digitalWrite(BUZZER, HIGH);
    digitalWrite(LED, HIGH);
    delay(TIME_DELAY);
    
    digitalWrite(BUZZER, LOW);
    digitalWrite(LED, LOW);
    delay(TIME_DELAY);
    
    digitalWrite(BUZZER, HIGH);
    digitalWrite(LED, HIGH);
    delay(TIME_DELAY);
    
    digitalWrite(BUZZER, LOW);
    digitalWrite(LED, LOW);
    delay(TIME_DELAY);
    
    digitalWrite(BUZZER, HIGH);
    digitalWrite(LED, HIGH);
    delay(TIME_DELAY);
    
    digitalWrite(BUZZER, LOW);
    digitalWrite(LED, LOW);
    delay(TIME_DELAY);
}
