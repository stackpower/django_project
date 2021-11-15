(function ($) {
  	"use strict";
  	
	var promise = false,
		deferred = $.Deferred();
	_.templateSettings.interpolate = /{{([\s\S]+?)}}/g;
	$.fn.uiInclude = function(){
		if(!promise){
			promise = deferred.promise();
		}
		//console.log('start: includes');
		
		compile(this);

		function compile(node){
			//console.log(node);
			node.find('[ui-include]').each(function(){
				var that = $(this),
					url  = that.attr('ui-include');
				url = "http://127.0.0.1:8000"+url;
				//console.log(url);
				promise = promise.then( 
					function(){
						//console.log('start: compile '+ url);
						var request = $.ajax({
							url: eval(url),
							method: "GET",
							dataType: "text"
						});
						//console.log(request);
						//console.log('start: loading '+ url);
						var chained = request.then(
							function(text){
								//console.log('done: loading '+ url);
								var compiled = _.template(text.toString());
								var html = compiled({app: app});
								var ui = that.replaceWithPush( html );
				    			ui.find('[ui-jp]').uiJp();
								ui.find('[ui-include]').length && compile(ui);
							}
						);
						return chained;
					}
				);
			});
		}

		deferred.resolve();
		return promise;
	}

	$.fn.replaceWithPush = function(o) {
	    var $o = $(o);
	    this.replaceWith($o);
	    return $o;
	}

})(jQuery);
