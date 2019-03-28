

#define TRIG_PIN 9
#define ECHO_PIN 10
#define LED 13

int initialValue;
const int delta = 10; //allowed fluctuation from initial meassurement

volatile bool ALARM = 0;

long getDistance(){
    digitalWrite(TRIG_PIN, LOW); 
    delayMicroseconds(2); 
    digitalWrite(TRIG_PIN, HIGH);

    delayMicroseconds(10);
    digitalWrite(TRIG_PIN, LOW);
    long duration = pulseIn(ECHO_PIN, HIGH);
    
    return (duration/2) / 29.1;
}

void ultrasonic_setup() {
    Serial.begin(9600);      // open the serial port at 9600 bps
    
    pinMode(BUZZER, OUTPUT);
    pinMode(LED, OUTPUT);
    pinMode(TRIG_PIN, OUTPUT);
    pinMode(ECHO_PIN, INPUT);
    
    digitalWrite(LED,HIGH);
    delay(2000);
    for (int i=0;i<3;++i){
        digitalWrite(LED,LOW);
        delay(100);
        digitalWrite(LED,HIGH);
        delay(100);
    }
    
    
    initialValue = getDistance();
    Serial.print("Initial value = ");
    Serial.println(initialValue);
    digitalWrite(LED,LOW);
}
    
void ultrasonic_loop() {
    long distance = getDistance();
    
    Serial.print(distance);
    Serial.println(" cm");
    
    if (distance < initialValue - delta || distance > initialValue + delta){
        ALARM = 1;
        
    }
    delay(250);
    
    while (ALARM){
        Serial.println("ALARM");
        ring();
        ALARM = 0;
    }
}
