"use strict";

$(function(){

  $( "#refresh_form" ).dialog({
    autoOpen: false,
    title: "Bitcoin.de trading API key",
    //      height: 400,
    width: "auto",
    //      modal: true,
    buttons: {
      "Get latest trades": function(){
        $("#refresh_form").submit();
      },
      "Cancel": function() {
        $(this).dialog( "close" );
      }
    },
    close: function(){
      $("#refresh_form")[0].reset();
    }
  });

  $("#api_key_form_toggle").button( {
    icon: "ui-icon-gear"
  } ).click(function(){
    $( "#refresh_form" ).dialog("open");
  });

  $("#refresh_form").on( "submit", function( event ) {
    event.preventDefault();
    var refresh_form = this;
    $.ajax({
      type: "POST",
      url: "/retrieve",
      data: $(refresh_form).serialize(),
      beforeSend: function(jqXHR, settings ){
        $("#refresh_form > input").prop("disabled",true);
        $("button.ui-button").prop("disabled",true);
        $("#refresh_form > .spinner").css("visibility", "visible");
      },
      error: function(jqXHR, textStatus, errorThrown ){
        $("#refresh_msg").text("Ajax Error: " + textStatus + ": " + errorThrown);
      },
      success: function(data)
      {
        var msg ="";
        if (typeof data === "undefined" || typeof data.status === "undefined"){
          msg = "Malformed response";
        }
        else if (data.status != 200){
          msg = "Error";
          if(typeof data.msg != "undefined")
            msg += ": " + data.msg;
        }else{
          msg = data.inserted + " new transactions written to DB"
        }
        $("#refresh_msg").text(msg);
      },
      complete: function(jqXHR, textStatus ){
        // called after error/success
        $("#refresh_form > input").prop("disabled",false);
        $("button.ui-button").prop("disabled",false);
        $("#refresh_form > .spinner").css("visibility", "hidden");
      }
    });
  });
});