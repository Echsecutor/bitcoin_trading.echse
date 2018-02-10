"use strict";

var chart;

//
function init_chart(){
  var ctx = $("#chart");

  var options = {
    maintainAspectRatio: false,
    scales: {
      yAxes: [{
        stacked: true,
        gridLines: {
          color: "rgba(255,255,255,0.5)"
        }
      }],
      xAxes: [{
        type: 'category',
        gridLines: {
          color: "rgba(255,255,255,0.5)"
        }
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
    data: {},
    options: options
  });

}

function load_chart(){

  $.ajax({
    type: "GET",
    url: "/chart",
    beforeSend: function(jqXHR, settings ){
      $("#chart_spinner").css("visibility", "visible");
    },
    error: function(jqXHR, textStatus, errorThrown ){
      $("#chart_msg").text("Ajax Error: " + textStatus + ": " + errorThrown);
    },
    success: function(data, textStatus)
    {
      chart.data = data.chart_data;
      chart.update();
      console.log("new chart data:");
      console.log(chart.data);
    },
    complete: function(){
      $("#chart_spinner").css("visibility", "hidden");
    }
  });

}




// fetching html
function load_data_table(){

  $.ajax({
    type: "GET",
    url: "/data",
    beforeSend: function(jqXHR, settings ){
      $("#data_table").prepend($("<span class='spinner'></span>").css("visibility", "visible"));
    },
    error: function(jqXHR, textStatus, errorThrown ){
      $("#data_table").text("Ajax Error: " + textStatus + ": " + errorThrown);
    },
    success: function(data, textStatus)
    {
      $("#data_table").html(data);
    }
  });
}



$(function () {
  init_chart();
  load_chart();

  load_data_table();
});