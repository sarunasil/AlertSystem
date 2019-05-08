Vue.http.options.root = 'http://' + window.location.hostname + ":" + "8080";

var app = new Vue({
    el: '#app',
    data: {
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
        this.refreshReceivers();
    },
    methods: {
       refreshReceivers() {
            this.$http.get('receivers', {headers: {'Authorization': 'Bearer ' + this.token}}).then(response => {
                this.receivers = response.body;
            }, response => {
                console.log(response.body);
                this.receivers = [];
            });
       },
       refreshContent(e){
            this.$http.get('alarms', {headers: {'Authorization': 'Bearer ' + this.token}}).then(response => {
                this.log_content = response.body;
            }, response => {
                console.log(response.body);
                this.log_content = '';
            });
            this.$refs.log_content_button.blur();
       },
       createAccount(e) {
              this.$http.post('register', {'username': this.new_username, 'password': this.new_password}, {headers: {'Authorization': 'Bearer ' + this.token}}).then(response => {
                  this.new_username = '';
                  this.new_password = '';
              }, response => {
                  console.log(response.body);
                  this.new_username = '';
                  this.new_password = '';
              });
              this.$refs.new_account_button.blur();
       },
       createFakeAlert(e) {
              this.$http.post('alarms?with_email='+this.with_email, {'msg': this.alert_message}, {headers: {'Authorization': 'Bearer ' + this.token}}).then(response => {
                  this.alert_message = '';
              }, response => {
                  console.log(response.body);
                  this.alert_message = '';
              });
              this.$refs.new_account_button.blur();
       },
       fetchToken(e) {
              this.$http.post('login', {'username': this.username, 'password': this.password}).then(response => {
                  this.username = '';
                  this.password = '';
                  this.token = response.body["token"];
                  this.refreshReceivers();
              }, response => {
                  console.log(response.body);
                  this.username = '';
                  this.password = '';
              });
              this.$refs.authentication_button.blur();
       },
       createReceiver(e) {
              if (this.email !== ''){
                  this.$http.post('receivers', {'email': this.email}, {headers: {'Authorization': 'Bearer ' + this.token}}).then(response => {
                      this.email = '';
                      this.refreshReceivers();
                  }, response => {
                      console.log(response.body);
                      this.email = '';
                  });
              }
              this.$refs.create_button.blur();
       },
       deleteReceivers(e) {
          this.$http.delete('receivers', {headers: {'Authorization': 'Bearer ' + this.token}}).then(response => {
            this.refreshReceivers();
          }, response => {
            console.log(response.body);
          });
          this.$refs.delete_all_button.blur();
       },
       deleteReceiver(receiverID){
          this.$http.delete('receivers/' + receiverID, {headers: {'Authorization': 'Bearer ' + this.token}}).then(response => {
            this.refreshReceivers();
          }, response => {
            console.log(response.body);
          });
       },
       getVisualisationKey(e) {
          this.$http.get('visualisation', {headers: {'Authorization': 'Bearer ' + this.token}}).then(response => {
            this.visualisation_key = response.body["key"];
          }, response => {
            console.log(response.body);
          });
          this.$refs.visualisation_key_button.blur();
       }
    }
});