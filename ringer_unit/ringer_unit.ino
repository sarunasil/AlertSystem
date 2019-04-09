
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
    
    if (response.indexOf(RESET_ALARM_COMMAND) >= 0){
        ring_status = 0;
        ble_send_reset_ack();
    }
    else if (response.indexOf(RING_COMMAND) >= 0){
        ring_status = 1;
        ble_send_ack();
    }
}


void setup() {
    setup_connection();
    ringer_setup();
    Serial.println("Setup done");
}

void loop() {

    if (debug){
        from_bluetooth_to_serial();
    }
    else{    
        if (get_state()){
            hub_message = ble_listen();
            delay(50);
            react_to_hub_response(hub_message);
        }
        
        if (ring_status){
            ring();
        }
    
        delay(250);
    }
}
