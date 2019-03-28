  #include <SoftwareSerial.h>
  SoftwareSerial EEBlue(3,4); // RX | TX

String c = "";
int counter = 0;
  void setup()
  {
    Serial.begin(9600);
//    EEBlue.begin(38400);  //Baud Rate for command Mode. 
    EEBlue.begin(9600);
    Serial.println("Enter AT commands!");
    delay(100);
    EEBlue.println("AT+UART");
    delay(100);
//    EEBlue.begin(9600);
    delay(100);
    EEBlue.println("AT+PSWD");
    EEBlue.println("AT+RNAME");
  }
   
  void loop()
  {
   EEBlue.println("AT+UART");
    
    // Feed any data from bluetooth to Terminal.
    if (EEBlue.available()){
      Serial.println(EEBlue.read());
    }
    // Feed all data from termial to bluetooth
    if (Serial.available()){
      c = Serial.readString();
      EEBlue.println(c);
      Serial.println("sent: "+c);
    }
    delay(1000);
    counter+=1;
    Serial.println(counter);
  }
