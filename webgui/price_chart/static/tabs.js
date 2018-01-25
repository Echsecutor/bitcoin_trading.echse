"use strict";

$( function() {
  $( "#tabs" ).tabs({
    beforeLoad: function( event, ui ) {
      ui.jqXHR.fail(function() {
        ui.panel.html(
          "Error loading tab." );
      });
    }
  });
} );
