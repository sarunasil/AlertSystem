#include <SoftwareSerial.h>

#define ARDUINO_RX 3
#define ARDUINO_TX 4
#define STATE_PIN 7

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
    if (current_state != connection_state){
        connection_state = current_state;
        if (current_state){
            Serial.println("Connected");
        }
        else{
            Serial.println("Disconnected");
        }
    }
    
    return digitalRead(STATE_PIN);
}

void program_bluetooth(){
    if(current_state == 0 && Serial.available()){
        input = Serial.readString();
        Serial.print("Sending: ");
        Serial.println(input);
        BTSerial.print(input);
    }
    else{
        Serial.println("Can't program bluetooth module while it's connected");
    }
}
 
void from_bluetooth_to_serial(){
    //read from the HM-10 and print in the Serial
    if(BTSerial.available()){
        serial_console_byte = BTSerial.read();
        Serial.write(serial_console_byte);
        //    BTSerial.write(serial_console_byte);
    }
    
    //read from the Serial and print to the HM-10
    if(Serial.available()){
        input = Serial.readString();
        Serial.print("Sending: ");
        Serial.println(input);
        BTSerial.print(input);
    }
}
