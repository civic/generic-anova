
import moment from 'moment';
import Chart from 'chart.js';
import Vue from 'vue';

export default Vue.component('chart-panel', {
  props: ['target', 'time_range'],
  template: '<div><canvas id="chart" height="250" style="border: 1px solid black;max-width: 400px;max-height:300px;"></canvas></div>',

  watch: {
    'time_range': function(v){
      if (v === 0){
        delete this.myChart.options.scales.xAxes[0].time.min;
        delete this.myChart.options.scales.xAxes[0].time.stepSize;
      } else {
        this.myChart.options.scales.xAxes[0].time.min = moment().subtract(v, 'minutes');
        if (v === 10){
          this.myChart.options.scales.xAxes[0].time.stepSize = 2;
        } else{
          this.myChart.options.scales.xAxes[0].time.stepSize = 10;
        }
      }
      this.myChart.update();
    }
  },
  methods: {
    set_data: function(data){
      var data_list1 = [];
      var data_list2 = [];
      var data_list3 = [];
      data.forEach( d => {
        data_list1.push({x: d["t"], y: d["y1"]});
        data_list2.push({x: d["t"], y: d["y2"]});
        data_list3.push({x: d["t"], y: d["p"]});
      });
      this.myChart.data.datasets[0].data = data_list1;
      this.myChart.data.datasets[1].data = data_list2;
      this.myChart.data.datasets[2].data = data_list3;
      this.myChart.update();
    },
    push_data: function(d){
      this.myChart.data.datasets[0].data.push({x: d["t"], y: d["y1"]});
      this.myChart.data.datasets[1].data.push({x: d["t"], y: d["y2"]});
      this.myChart.data.datasets[2].data.push({x: d["t"], y: d["p"]});
      
      if (this.time_range === 0){
        delete this.myChart.options.scales.xAxes[0].time.min;
      } else {
        this.myChart.options.scales.xAxes[0].time.min = moment().subtract(this.time_range, 'minutes');
      }
      this.myChart.update();
    }
  },
  mounted: function() {
    const ctx = document.getElementById('chart');

    this.myChart = new Chart(ctx, {
      type: 'line',
      data: {
        datasets: [
          {
            label: '水温',
            backgroundColor: 'rgba(255, 99, 132, 0.1)',
            borderColor: 'rgba(255, 99, 132, 0.8)',
            pointRadius: 0,
            borderWidth: 2,
            yAxisID: 'y-temperature',
          },
          {
            label: '基盤温度',
            borderColor: 'rgba(50, 19, 132, 0.8)',
            pointRadius: 0,
            fill: false,
            borderWidth: 2,
            yAxisID: 'y-temperature',
          },
          {
            label: '出力',
            borderColor: 'rgba(10, 99, 132, 0.8)',
            pointRadius: 0,
            fill:false,
            borderWidth: 2,
            yAxisID: 'y-output',
          }
        ]
      },
      options: {
        animation: {
          duration: 0
        },
        elements: {
          line: {
            tension: 0
          }
        },
        scales: {
          xAxes: [
            {
              type: 'time',
              time: {
                unit: 'minute',
                displayFormats: { minute: 'H:mm' },
                tooltipFormat: 'HH:mm:ss'
              },
            }
          ],
          yAxes: [ 
            { 
              id: "y-temperature",
              ticks: { min: 30, max: 80 } 
            }, 
            { 
              id: "y-output",
              display: false,
              ticks: { min: 0, max: 300 } 
            } 
          ]
        }
      }
    });
  }
});
