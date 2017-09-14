class GenericAnovaModel {
  constructor(){
    this.current_temperature = 61.0;
    this.target_temperature = 20.0;
    this.past_time = 60*60*1 + 12*60;
    this.left_seconds = 0;
    this.end_time = new Date("2017-9-1 13:40");
    this.last_update = null;
    this.set_hours = 2;
    this.set_minutes = 30;
    this.control_state = 'stop';
    this.power=0;
    this.time_range = 0;
  }
  index(){
    return fetch_json('/api/index').then(info => {
      this.control_state = info['control_state'];
      this.target_temperature = info['target_temperature'];
      this.current_temperature = info["current_temperature"];
      this.last_update = new Date();
      this.chart_data = info["chart_data"];
      this.set_hours = info["set_hours"];
      this.set_minutes = info["set_minutes"];

      this.past_seconds = info["past_seconds"];
      this.left_seconds = info["left_seconds"];
      this.end_time = new Date(info["end_time"]);
      this.power = info["power"];
    });
  }
  update_newdata(newdata){
      this.current_temperature = newdata["y1"]
      this.last_update = new Date();
  }

  update_target_temperature(val){
    return fetch_json('/api/pid', 'PUT', {
      'target_temperature': val
    }).then(info => {
      this.control_state = info['control_state'];
      this.power=info["power"];
    });
  }

  clear(){
    return fetch_json('/api/temperature', 'DELETE').then(()=>{
      this.chart_data = [];
      this.last_update = new Date();
    });
  }

  set_control_start(){
    return fetch_json('/api/pid', 'PUT', {
      'control_state': 'start',
      'set_hours': this.set_hours,
      'set_minutes': this.set_minutes
    }).then(info=>{
      this.control_state = info['control_state'];
      this.target_temperature = info['target_temperature'];

      this.set_hours = info["set_hours"];
      this.set_minutes = info["set_minutes"];

      this.past_seconds = info["past_seconds"];
      this.left_seconds = info["left_seconds"];
      this.end_time = new Date(info["end_time"]);
      this.power=info["power"];

    });
  }
  set_timer_pause(){
    return fetch_json('/api/pid', 'PUT', {
      'control_state': 'pause',
    }).then(info=>{
      this.control_state = info['control_state'];
      this.target_temperature = info['target_temperature'];

      this.set_hours = info["set_hours"];
      this.set_minutes = info["set_minutes"];

      this.power=info["power"];
    });
  }
  set_control_stop(){
    return fetch_json('/api/pid', 'PUT', {
      'control_state': 'stop',
    }).then(info=>{
      this.control_state = info['control_state'];
      this.past_seconds = info["past_seconds"];
      this.left_seconds = info["left_seconds"];
      this.end_time = new Date(info["end_time"]);
      this.power=info["power"];

    });
  }
  past(seconds){
    if (seconds - this.past_seconds > 30){
      //長時間経過しているのでsseからの更新データではなく
      //indexから全データを更新(一時的にオフラインだった可能性)
      this.index();
    } else {
      this.past_seconds = seconds;
      this.left_seconds = (this.set_hours * 3600 + this.set_minutes * 60) - seconds;
      this.last_update = new Date();
    }
  }
};

function fetch_json(url, method, data){
  const options = {
    headers: {
      "Content-Type": "application/json"
    },
    method: method ? method : "GET",
  };
  if (data){
    options["body"] = JSON.stringify(data);
  }
  return fetch(url, options).then(response => response.json());
}
export default GenericAnovaModel;
