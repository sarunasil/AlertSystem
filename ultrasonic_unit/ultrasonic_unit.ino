
#define RESET_ALARM_COMMAND "RESET\n"
#define RESET_AND_MEASURE_COMMAND "RESEET_AND_MEASURE\n"
#define ACK_COMMAND "ACK\n"

#define SEPARATOR_CHAR '\n'
//MAIN FILE

//alarm_status codes:
//  0 - no alarm, measuring
//  1 - alarm, sending msg to hub
//  2 - alarm, hub received msg, not sending, but not measuring as well

int alarm_status = 0;
String hub_response = "";

bool debug = 0;

void react_to_hub_response(String response){

    Serial.print("Response = '");
    Serial.print(response);
    Serial.println("'");

    
//    if (alarm_status == 2 && response.indexOf(RESET_ALARM_COMMAND) >= 0){
    if (response.indexOf(RESET_ALARM_COMMAND) >= 0){
        alarm_status = 0;
        ble_send_reset_ack();
    }
//    else if (alarm_status == 2 && response.indexOf(RESET_AND_MEASURE_COMMAND) >= 0){
    else if (response.indexOf(RESET_AND_MEASURE_COMMAND) >= 0){
        alarm_status = 0;
        set_initial_value();
        ble_send_reset_ack();
    }
    else if (response.indexOf(ACK_COMMAND) >= 0 && alarm_status == 1){
        alarm_status = 2;
    }
}


void setup() {
    setup_connection();
    ultrasonic_setup();
}

void loop() {

    if (debug){
        from_bluetooth_to_serial();
    }
    else{    
        if (get_state()){
            hub_response = ble_listen();
            react_to_hub_response(hub_response);
            delay(50);
            
            alarm_status = check_alarm();
    
            while (alarm_status){
                get_state();
                if (alarm_status == 1){
                    ble_send_alarm();
                }
                delay(1000);
    
                hub_response = ble_listen();
                react_to_hub_response(hub_response);
                delay(50);
            }
        }
        else{
            delay(1000);
        }
    
        delay(200);
    }
}
