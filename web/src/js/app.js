'use strict'

import Vue from 'vue';
import ChartPanel from './chart-panel.js';
import numeral from 'numeral';
import moment from 'moment';
import GenericAnovaModel from './model.js';

const ga_model = new GenericAnovaModel();

ga_model.index().then(()=>{

  const eventSource = new EventSource("/sse");
  eventSource.onmessage = e=>{
    const evt = JSON.parse(e.data);
    app.receive(evt);
  };

  const app = new Vue({
    data: ga_model,
    el: '#app',
    template: '#my-template',
    watch: {
      'target_temperature': function(val){
        ga_model.update_target_temperature(val);
      }
    },
    methods: {
      set_control_state: function(evt){
      },
      clear: function(evt){
        ga_model.clear().then(()=>{
          this.chart.set_data(ga_model.chart_data);
        });
      },
      timer_start: function(evt){
        ga_model.set_control_start();
      },
      timer_pause: function(evt){
        ga_model.set_timer_pause();
      },
      timer_stop: function(evt){
        ga_model.set_control_stop();
      },
      receive: function(evt){
        if (evt.event === "newdata"){
          ga_model.update_newdata(evt["data"]);
          ga_model.past(evt['past_seconds']);
          ga_model.power = evt["power"];
          this.chart.push_data(evt["data"]);
        }
      },
      reload: function(evt){
        window.location.reload();
      }
    },
    filters: {
      numberFormat: num =>numeral(num).format('0.0'),
      timetermFormat: time => {
        if (time <=0){
          return "0h 0m";
        }
        if (time%60 >= 30){
          const t = time + 30;
          return parseInt(t/3600) + "h " + parseInt((t%3600)/ 60) + "m";
        } else {
          return parseInt(time/3600) + "h " + parseInt((time%3600)/ 60) + "m";
        }
      },
      timeFormat: (time, fmt) => moment(time).format(fmt)
    },
    mounted: function(){
      this.chart = this.$refs.chart;
      this.chart.set_data(ga_model.chart_data);
    },
  });
});
