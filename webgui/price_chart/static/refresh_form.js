"use strict";

$(function(){
  $("#refresh_form").on( "submit", function( event ) {
    event.preventDefault();
    var refresh_form = this;
    $.ajax({
      type: "POST",
      url: "/retrieve",
      data: $(refresh_form).serialize(),
      beforeSend: function(jqXHR, settings ){
        $("#refresh_form > input").prop("disabled",true);
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
            msg += ": " + msg;
        }else{
          msg = data.inserted + " new transactions written to DB"
        }
        $("#refresh_msg").text(msg);
      },
      complete: function(jqXHR, textStatus ){
        // called after error/success
        $("#refresh_form > input").prop("disabled",false);
      }
    });
  });
});