
#define RESET_ALARM_COMMAND "RESET\n"
#define RING_COMMAND "RING\n"
//MAIN FILE

bool ring_status = 0;
String hub_message = "";

bool debug = 0;

void react_to_hub_response(String response){

    Serial.print("Response = '");
    Serial.print(response);
    Serial.println("'");
    
    Serial.print("COMMAND = '");
    Serial.print(RESET_ALARM_COMMAND);
    Serial.println("'");
    if (response == RESET_ALARM_COMMAND){
        ring_status = 0;
    }
    else if (response == RING_COMMAND){
        ring_status = 1;
    }
}


void setup() {
    setup_connection();
    ringer_setup();
}

void loop() {

    if (debug){
        from_bluetooth_to_serial();
    }
    else{    
        if (get_state()){
            hub_message = ble_listen();
            react_to_hub_response(hub_message);

            if (ring_status){
                ring();
            }
            delay(2000);
        }
    
        delay(250);
    }
}
