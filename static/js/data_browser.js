
var cache = {}; //all used urls and results are stored here to cache already done searches
var cache_files =  {};
var data_browser;

data_browser = new function(){
	this.rows = 100;
	this.url = '/solr/solr-search/';
	this.query = {};
	
	this.get_query = function(){
		result = '';
		$.each(this.query,function(key,val){
			result += '&'+key+'='+val;
		});
		return result;
	};

	this.get_facets = function(){
		var url = this.url + '?facet=*' + this.get_query();
		//simple cache function
		if (!(url in cache)) {
			var answer 
			var acall = $.ajax(url, {
        	            async: false,
     	 	            dataType: 'json',
       		            success: function(response){
				answer = response;
       		            }
	            	});
        	    	cache[url] = answer;
		}	
                this.update_container(cache[url]);

	};
	
	this.get_files = function(){
		var url = this.url + '?start=0&rows='+this.rows+this.get_query();
		if (!(url in cache_files)) {
		   $.ajax(url, {
            		dataType: 'json',
            		success: function(response){
				    cache_files[url]=response;
				    data_browser.update_files_container(cache_files[url]);
				}
       			});
		}else{
		   this.update_files_container(cache_files[url]);
		}
	};	

	this.add_facet = function(facet,value){
		this.query[facet] = value;
		this.get_facets();
	};

	this.remove_facet = function(facet){
		delete this.query[facet];
		this.get_facets();
	};

	this.update_files_container = function(answer){
		$('#headingFiles .files_count').html('('+answer['metadata']['numFound']+')');	
		var result_list = '<div style="max-height:500px; overflow:auto;"><ul class="jqueryFileTree">';
		$.each(answer['data'],function(key,val){
			result_list += '<li class="file ext_nc" style="margin-bottom:5px;">'+val+'</li>';
		});
		result_list += '</ul></div>';
		$('#collapseFiles').children().html(result_list);
	};

	this.update_container = function(answer){
	    selected_html = '';
	    $.each(answer['data'],function(facet,facet_list){
		if(facet_list.length == 0){
			$('#heading'+facet).parent().parent().hide();
			return
		}
		
		$('#heading'+facet).parent().parent().show();
		$('#heading'+facet+' .facet_count').html('('+facet_list.length/2+')');
		html = '<div class="row">';
		$.each(facet_list,function(val)
		{
		   if(val%2==0){
		      if(facet in data_browser.query){	
			var del_link = '<a href="#" class="facet_remove" data-facet="'+facet+'"><span class="glyphicon glyphicon-remove-circle"></span></a>';
		        html += '<div class="col-md-3">'+del_link+' <strong>'+facet_list[val]+'</strong> ('+facet_list[val+1]+')</div>';	
			$('#heading'+facet+' .chosen_facet').html(': <strong>'+ facet_list[val]+'</strong> '+del_link);
			$('#heading'+facet+' .facet_count').html('');
			//updated selected panel
			selected_html += del_link + ' '+facet+ ':<strong>'+facet_list[val]+'</strong>; ';
		      }else{
                        html += '<div class="col-md-3"><a class="facet_click" data-facet="'+facet+'" href="#">'+facet_list[val]+'</a> ('+facet_list[val+1]+')</div>';
			$('#heading'+facet+' .chosen_facet').html('');
	 	      }

		   }
		});
		html += '</div>';
		var collapsediv = $('#collapse'+facet);
		collapsediv.children().html(html);
	     });

	     //Show or hide selected panel+
	     if(selected_html == '')
		$('#facet_selected').parent().hide();
	     else
		$('#facet_selected').parent().show();
	     $('#facet_selected').html(selected_html);
	};


}


