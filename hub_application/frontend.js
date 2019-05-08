Vue.http.options.root = 'http://' + window.location.hostname + ":" + "8080";

var app = new Vue({
    el: '#app',
    data: {
      sensors: [],
      ringers: [],

      token: "",
      username: "",
      password: "",

      sensor_alias: "",
      sensor_mac: "",
      ringer_alias: "",
      ringer_mac:"",

      measure_flag: false,
      scan_content: ""
    },
    mounted: function(){
        this.refreshSensors();
        this.refreshRingers();
    },
    methods: {
       requestScanContent(e){
            this.$http.post('devices/scanning', {}, {headers: {'Authorization': 'Bearer ' + this.token}}).then(response => {
                console.log(response.body);
            }, response => {
                console.log(response.body);
            });
            this.$refs.request_scan_content_button.blur();
       },
       refreshScanContent(e) {
            this.$http.get('devices/scanning', {headers: {'Authorization': 'Bearer ' + this.token}}).then(response => {
                this.scan_content = response.body;
            }, response => {
                console.log(response.body);
            });
            this.$refs.refresh_scan_content_button.blur();
       },
       refreshSensors() {
            this.$http.get('devices/sensors', {headers: {'Authorization': 'Bearer ' + this.token}}).then(response => {
                this.sensors = response.body;
            }, response => {
                console.log(response.body);
                this.sensors = [];
            });
       },
       refreshRingers() {
            this.$http.get('devices/ringers', {headers: {'Authorization': 'Bearer ' + this.token}}).then(response => {
                this.ringers = response.body;
            }, response => {
                console.log(response.body);
                this.ringers = [];
            });
       },
       fetchToken(e) {
              this.$http.post('login', {'username': this.username, 'password': this.password}).then(response => {
                  this.username = '';
                  this.password = '';
                  this.token = response.body["token"];
                  this.refreshSensors();
                  this.refreshRingers();
              }, response => {
                  console.log(response.body);
                  this.username = '';
                  this.password = '';
              });
              this.$refs.authentication_button.blur();
       },
       createSensor(e) {
              if (this.sensor_alias !== '' && this.sensor_mac != ''){
                  this.$http.post('devices/sensors', {'alias': this.sensor_alias, 'mac': this.sensor_mac}, {headers: {'Authorization': 'Bearer ' + this.token}}).then(response => {
                      this.sensor_alias = '';
                      this.sensor_mac = '';
                      this.refreshSensors();
                  }, response => {
                      console.log(response.body);
                      this.sensor_alias = '';
                      this.sensor_mac = '';
                  });
              }

              this.$refs.create_sensor_button.blur();
       },
       createRinger(e) {
              if (this.ringer_alias !== '' && this.ringer_mac != ''){
                  this.$http.post('devices/ringers', {'alias': this.ringer_alias, 'mac': this.ringer_mac}, {headers: {'Authorization': 'Bearer ' + this.token}}).then(response => {
                      this.ringer_alias = '';
                      this.ringer_mac = '';
                      this.refreshRingers();
                  }, response => {
                      console.log(response.body);
                      this.ringer_alias = '';
                      this.ringer_mac = '';
                  });
              }

              this.$refs.create_ringer_button.blur();
       },
       deleteSensors(e) {
          this.$http.delete('devices/sensors', {headers: {'Authorization': 'Bearer ' + this.token}}).then(response => {
            this.refreshSensors();
          }, response => {
            console.log(response.body);
          });
          this.$refs.delete_all_sensors_button.blur();
       },
       deleteRingers(e) {
          this.$http.delete('devices/ringers', {headers: {'Authorization': 'Bearer ' + this.token}}).then(response => {
            this.refreshRingers();
          }, response => {
            console.log(response.body);
          });
          this.$refs.delete_all_ringers_button.blur();
       },
       deleteSensor(sensorID){
          this.$http.delete('devices/sensors/' + sensorID, {headers: {'Authorization': 'Bearer ' + this.token}}).then(response => {
            this.refreshSensors();
          }, response => {
            console.log(response.body);
          });
       },
       deleteRinger(ringerID){
          this.$http.delete('devices/ringers/' + ringerID, {headers: {'Authorization': 'Bearer ' + this.token}}).then(response => {
            this.refreshRingers();
          }, response => {
            console.log(response.body);
          });
       },
       resetAlert(e){
          this.$http.delete('alarms?measure=' + this.measure_flag, {headers: {'Authorization': 'Bearer ' + this.token}}).then(response => {
            console.log(response.body);
          }, response => {
            console.log(response.body);
          });
          this.$refs.reset_alert_button.blur();
       }
    }
});