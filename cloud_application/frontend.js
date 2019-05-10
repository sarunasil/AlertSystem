Vue.http.options.root = 'http://' + window.location.hostname + ":" + "8080";

var app = new Vue({
    el: '#app',
    data: {
      info_msg: "",
      receivers: [],
      token: "",
      username: "",
      password: "",
      new_username: "",
      new_password: "",
      email: "",
      log_content: "",
      visualisation_key: "None",
      alert_message: "",
      with_email: false
    },
    mounted: function(){
        this.info_msg = "Please authenticate to retrieve a JWT token.";
    },
    methods: {
       refreshReceivers() {
            this.$http.get('receivers', {headers: {'Authorization': 'Bearer ' + this.token}}).then(response => {
                this.receivers = response.body;
                this.info_msg = "";
            }, response => {
                this.info_msg = response.body;
            });
       },
       refreshContent(e){
            this.$http.get('alarms', {headers: {'Authorization': 'Bearer ' + this.token}}).then(response => {
                this.log_content = response.body;
                this.info_msg = "";
            }, response => {
                this.info_msg = response.body;
            });
            this.$refs.log_content_button.blur();
       },
       createAccount(e) {
              this.$http.post('register', {'username': this.new_username, 'password': this.new_password}, {headers: {'Authorization': 'Bearer ' + this.token}}).then(response => {
                  this.info_msg = "";
              }, response => {
                  this.info_msg = response.body;
              });
              this.$refs.new_account_button.blur();
              this.new_username = '';
              this.new_password = '';
       },
       createFakeAlert(e) {
              this.$http.post('alarms?with_email='+this.with_email, {'msg': this.alert_message}, {headers: {'Authorization': 'Bearer ' + this.token}}).then(response => {
                  this.info_msg = "";
              }, response => {
                  this.info_msg = response.body;
              });
              this.$refs.new_account_button.blur();
              this.alert_message = '';
       },
       fetchToken(e) {
              this.$http.post('login', {'username': this.username, 'password': this.password}).then(response => {
                  this.token = response.body["token"];
                  this.info_msg = "";
                  this.refreshReceivers();
              }, response => {
                  this.info_msg = response.body;
              });
              this.$refs.authentication_button.blur();
              this.username = '';
              this.password = '';
       },
       createReceiver(e) {
              this.$http.post('receivers', {'email': this.email}, {headers: {'Authorization': 'Bearer ' + this.token}}).then(response => {
                  this.info_msg = "";
                  this.refreshReceivers();
              }, response => {
                  this.info_msg = response.body;
              });
              this.$refs.create_button.blur();
              this.email = '';
       },
       deleteReceivers(e) {
          this.$http.delete('receivers', {headers: {'Authorization': 'Bearer ' + this.token}}).then(response => {
            this.info_msg = "";
            this.refreshReceivers();
          }, response => {
            this.info_msg = response.body;
          });
          this.$refs.delete_all_button.blur();
       },
       deleteReceiver(receiverID){
          this.$http.delete('receivers/' + receiverID, {headers: {'Authorization': 'Bearer ' + this.token}}).then(response => {
            this.info_msg = "";
            this.refreshReceivers();
          }, response => {
            this.info_msg = response.body;
          });
       },
       getVisualisationKey(e) {
          this.$http.get('visualisation', {headers: {'Authorization': 'Bearer ' + this.token}}).then(response => {
            this.info_msg = "";
            this.visualisation_key = response.body["key"];
          }, response => {
            this.info_msg = response.body;
          });
          this.$refs.visualisation_key_button.blur();
       }
    }
});