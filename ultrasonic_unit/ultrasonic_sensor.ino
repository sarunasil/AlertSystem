

#define TRIG_PIN 9
#define ECHO_PIN 10
#define LED 13

int initialValue;
const int delta = 10; //allowed fluctuation from initial meassurement

long getDistance(){
    digitalWrite(TRIG_PIN, LOW); 
    delayMicroseconds(2); 
    digitalWrite(TRIG_PIN, HIGH);

    delayMicroseconds(10);
    digitalWrite(TRIG_PIN, LOW);
    long duration = pulseIn(ECHO_PIN, HIGH);
    
    return (duration/2) / 29.1;
}

void set_initial_value(){
    initialValue = getDistance();
    Serial.print("Initial value = ");
    Serial.println(initialValue);
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
    
    set_initial_value();
    digitalWrite(LED,LOW);
}
    
bool check_alarm() {
    long distance = getDistance();
    
    Serial.print(distance);
    Serial.println(" cm");
    
    if (distance < initialValue - delta || distance > initialValue + delta){
        ring();
        return 1;
        
    }

    return 0;
}
