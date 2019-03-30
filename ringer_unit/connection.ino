#include <SoftwareSerial.h>

#define ARDUINO_RX 3
#define ARDUINO_TX 4
#define STATE_PIN 6

SoftwareSerial BTSerial(ARDUINO_RX, ARDUINO_TX); //RX|TX

// it goes to AT mode without EN pin immediatelly
// needs /r/n obviously, the bound rate is always 9600
// managed to connect to BluetoothLE and BlueCap
// BluetoothLE even sent data to the service with FF
// no further service configurations is possible...
// can go to sleep mode - wake up with 80+ char string via serial
// AT+CONN[index]
// connects without pin

int connection_state = 0;
int current_state = 0;

String input = "";
int serial_console_byte = 0;
void setup_connection(){
    Serial.begin(9600);
    BTSerial.begin(9600); // default baud rate
    
    pinMode(STATE_PIN, INPUT);
    
    while(!Serial); //if it is an Arduino Micro
    Serial.println("Connection setup done.");
}

int get_state(){
  current_state = digitalRead(STATE_PIN);
    if (current_state != connection_state){
        connection_state = current_state;
        if (current_state){
            Serial.println("Connected");
        }
        else{
            Serial.println("Disconnected");
        }
    }
    
    return current_state;
}

void from_bluetooth_to_serial(){
    get_state();
    //read from the HM-10 and print in the Serial
    if(BTSerial.available()){
        input = BTSerial.readString();
        Serial.println(input);
    }
    
    //read from the Serial and print to the HM-10
    if(Serial.available()){
        input = Serial.readString();
        Serial.print("Sending: ");
        Serial.println(input);
        BTSerial.print(input);
    }
}

String ble_listen(){
    String msg = "";
    if(current_state && BTSerial.available()){
        msg = BTSerial.readString();
        Serial.println("HUB says: "+msg);
    }
    return msg;
}

//void ble_send_alarm(){
//    if (current_state){
//        Serial.println("Sending: ALARM");
//        BTSerial.print("ALARM");
//    }
//}
