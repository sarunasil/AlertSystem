#include <SoftwareSerial.h>
SoftwareSerial BTSerial(3, 4); //RX|TX

// it goes to AT mode without EN pin immediatelly
// needs /r/n obviously, the bound rate is always 9600
// managed to connect to BluetoothLE and BlueCap
// BluetoothLE even sent data to the service with FF
// no further service configurations is possible...
// can go to sleep mode - wake up with 80+ char string via serial
// AT+CONN[index]
// connects without pin

const int state_pin = 7;
int connection_state = 0;
int current_state = 0;

String input = "";
int serial_console_byte = 0;
void setup(){
  Serial.begin(9600);
  BTSerial.begin(9600); // default baud rate

  pinMode(state_pin, INPUT);
  
  while(!Serial); //if it is an Arduino Micro
  Serial.println("AT commands: ");
}
 
void loop(){
  current_state = digitalRead(state_pin);
  if (current_state != connection_state){
    connection_state = current_state;
    if (current_state){
      Serial.println("Connected");
    }
    else{
      Serial.println("Disconnected");
    }
  }

  //read from the HM-10 and print in the Serial
  if(BTSerial.available()){
    serial_console_byte = BTSerial.read();
    Serial.write(serial_console_byte);
//    BTSerial.write(serial_console_byte);
  }
  
  //read from the Serial and print to the HM-10
  if(Serial.available()){
    input = Serial.readString();
//    int i = Serial.read();
    Serial.print("Sending: ");
    Serial.println(input);
//    Serial.write(i);
    BTSerial.print(input);
//    BTSerial.write(i);
  }
}
