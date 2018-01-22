"use strict";

var chart;

function loadChart(chart_data){
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
    data: chart_data,
    options: options
  });

  console.log(chart.data);
}

