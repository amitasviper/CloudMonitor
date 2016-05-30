
var memory_series, cpu_series, network_series;
var friendly_name = {'cpu_stats': 'CPU Usage', 'memory_stats' : 'Memory Usage', 'network_stats' : 'Network Usage'};
var socket, cpu_count=1;
function get_data()
{
  console.log("calling for : ");
  var count = 0;
  socket.emit('channel_host_info_req', host_id);

  socket.on('channel_host_info_resp', function (data)
  {
    console.log("Data received from server : " + data);

    data = JSON.parse(data);

      x = (new Date()).getTime(); // current time

      //for memory graph
      y = data.memory;
      //console.log("The x and y values are : " + x + "  "+ y);
      memory_series[0].addPoint([x, y], true, true);

      y = data.cpu;
      //console.log("The x and y values are : " + x + "  "+ y);
      cpu_series[0].addPoint([x, y], true, true);

      y = data.network;
      network_series[0].addPoint([x, y], true, true);

    });

  setInterval(function(){socket.emit('channel_host_info_req', host_id);}, 1000);
}

function initialise_graphs(){
  console.log("Into the initialise phase");
  render_chart("#memory_usage_chart", memory_series, 'memory_stats');
  render_chart("#cpu_usage_chart", cpu_series, 'cpu_stats');
  render_chart("#network_usage_chart", network_series, 'network_stats');

  get_data();
}

function initialise(){

  console.log("The container id is :" +host_id);
  socket = io.connect('http://' + document.domain + ':' + location.port);
  
  initialise_graphs();
}


function render_chart(container_name, series_name, json_key) {
  $(document).ready(function () {
    Highcharts.setOptions({
      global: {
        useUTC: false
      }
    });

    $(container_name).highcharts({
      chart: {
        type: 'spline',
                animation: true, // don't animate in old IE
                marginRight: 10,
                events: {
                  load: function () {
                        // set up the updating of the chart each second
                        if(json_key == 'cpu_stats')
                        {
                          cpu_series = this.series;
                        }
                        else if( json_key == 'memory_stats')
                        {
                          memory_series = this.series;
                        }
                        else if (json_key == 'network_stats') 
                        {
                          network_series = this.series;
                        };
                        console.log("Size of the series " + this.series + " is : " + this.series.length);
                      }
                    }
                  },
                  title: {
                    text: friendly_name[json_key]
                  },
                  xAxis: {
                    type: 'datetime',
                    tickPixelInterval: 150
                  },
                  yAxis: {
                    title: {
                      text: 'Value'
                    },
                    plotLines: [{
                      value: 0,
                      width: 1,
                      color: '#808080'
                    }]
                  },
                  tooltip: {
                    formatter: function () {
                      return '<b>' + this.series.name + '</b><br/>' +
                      Highcharts.dateFormat('%Y-%m-%d %H:%M:%S', this.x) + '<br/>' +
                      Highcharts.numberFormat(this.y, 2);
                    }
                  },
                  legend: {
                    enabled: false
                  },
                  exporting: {
                    enabled: false
                  },
                  series: create_series_array(json_key)
                });
});
}

function create_series_array(json_key){
  var size = 1;
  console.log("Generating series for " + json_key);

  var temp_series = [];
  for (j = 0; j <size; j += 1){
    instance_series = {
      name: friendly_name[json_key] + ' #' + j,
      data: (function () {
                    // generate an array of random data
                    var data = [],
                    time = (new Date()).getTime(),
                    i;

                    for (i = -19; i <= 0; i += 1) {
                      data.push({
                        x: time + i * 1000,
                        y: Math.random()*100
                      });
                    }
                    return data;
                  }())
    }
    temp_series[j] = instance_series;
  }
  return temp_series;
}


function show(id, value) {
  document.getElementById(id).style.display = value ? 'block' : 'none';
}

$(document).ready(initialise);