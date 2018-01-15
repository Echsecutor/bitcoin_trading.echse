// example script using chartjs

"use strict";

var chart;

function sampleData(){
  var data={
    datasets: [
      {
        fill: '+1',
        label: "p1",
        data : []
      },
      {
        fill: '+1',
        label: "p2",
        data: []
      },
      {
        fill: '0',
        label: "p3",
        data: []
      },
    ]
  };

  for (var i = 0; i < 6; i++)
  {
    var x = 0;
    data.datasets.forEach(function(ds)
                          {
                            x += Math.random();;
                            ds.data.push(x);
                          }
                         );
  }
  
  data.labels= ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']

  return data;
}

function loadChart(){
  var ctx = $("#chart");

  var options = {
    maintainAspectRatio: false,
    scales: {
      yAxes: [{
        stacked: true
      }]
    },
    title:{
      display: true,
      text: 'Transaction data from bitcoin.de'
    },
    elements: {
      line: {
        // interpolation
	tension: 0.000001
      }
    }
  };

  chart = new Chart(ctx, {
    type: 'line',
    data: sampleData(),
    options: options
  });

  console.log(chart.data);
}

function setSampleData(){
  chart.data = sampleData();
  chart.update();
}


$(function(){
  loadChart();

  //for fun ;)
  $(".chart-container").click(setSampleData);
});