/** @jsx React.DOM */

var FacetItem = React.createClass({
	render : function(){
		var cx = React.addons.classSet;
		var classes = cx({
			'facet_tooltip': this.props.title,
		});
		return (
			<div className="col-md-3 col-xs-6">
				<a href="#" onClick={this.props.updateFacets.bind(null,this.props.facet_name,this.props.facet_value,'add')}i title={this.props.title} className={classes}>
					{this.props.facet_value}
				</a> [{this.props.files_count}]
			</div>
		);
	}

});

var AccordionItem = React.createClass({
	
	getInitialState: function(){
		return {search_value: ""}
	},
	
	search_list: function(event){
		this.setState({search_value: event.target.value});
	},
	
	componentDidUpdate: function(){
		$('.facet_tooltip').tooltip({'placement':'right','html':true,container: 'body'});
	},

	componentDidMount: function(){
		$('.facet_tooltip').tooltip({'placement':'right','html':true,container: 'body'});
	},

	render: function(){
		
		var facet_items = [];
		var self = this;
		var search_value = this.state.search_value.trim().toLowerCase();
		$.each(this.props.facet_list,function(i,val){
			if(i%2==0){
				var test_val = val.toLowerCase();
				if(window[self.props.facet_name] && window[self.props.facet_name][val])
				{	
					var metadata = window[self.props.facet_name];
					if(metadata[val].toLowerCase().indexOf(search_value) === -1 && test_val.indexOf(search_value) === -1)
						return
					else{
						facet_items.push(<FacetItem facet_value={val} files_count={self.props.facet_list[i+1]} 
                                                                        updateFacets={self.props.updateFacets} facet_name={self.props.facet_name} key={val} title={metadata[val]}/>);
                                        }
				}else{
					if(test_val.indexOf(search_value) === -1)
						return
					else{
						facet_items.push(<FacetItem facet_value={val} files_count={self.props.facet_list[i+1]} 
									updateFacets={self.props.updateFacets} facet_name={self.props.facet_name} key={val}/>);
					}
				}	
			}
		});
		
		var cx = React.addons.classSet;
		var classes = cx({
			'panel': true,
			'panel-default': true,
			'hidden': this.props.facet_list.length < 1
		});
		
		var facet_count = this.props.facet_list.length / 2;
		
		var item_title = [];
		var search_input = [];
		if(facet_count == 1){
			item_title.push(<span className="chosen_facet">: <strong>{this.props.facet_list[0]}</strong></span>);
			if(this.props.selected_facets[this.props.facet_name])
				item_title.push(<span className="chosen_facet"> 
									<a href="#" onClick={this.props.updateFacets.bind(null,this.props.facet_name,'','del')}> 
										 <span className="glyphicon glyphicon-remove-circle" />
									</a>
								</span>); 
		}else{
			item_title.push(<span className="facet_count">({facet_count}) </span>);
			search_input.push(<div className="col-md-12">
								<input id={this.props.facet_name+"_search"} name={this.props.facet_name+"_search"} className="form-control"
							 	placeholder={"Search " + this.props.facet_name + " name"} onChange={this.search_list} value={this.state.search_value}/>
							  </div>);
		}
		
		return (
			<div className={classes}>
			    <div className="panel-heading">
			      <h4 className="panel-title" id={"heading" + this.props.facet_name}>
			        <a data-toggle="collapse" data-parent="#accordion" href={"#collapse" + this.props.facet_name}>
			        	 {this.props.facet_name}
					</a>  {item_title}
			      </h4>
			    </div>
			
			  	<div id={"collapse" + this.props.facet_name} className="panel-collapse collapse">
			      <div className="panel-body">
					<div className="row">
						{search_input}
						{facet_items}
				
					</div>
				
			      </div>
			    </div>
			
			  </div>
		)
	}
});

var FileItem = React.createClass({
	openNcdump: function(e){
		$('#ncdump_file').val($(e.target).next().html());
		ncdumpDialog.show();
	},
		
	render: function(){
		var liStyle = {marginBottom:5};
		return (
			<li className="file ext_nc" style={liStyle}>
				<span className="ncdump glyphicon glyphicon-info-sign" onClick={this.openNcdump} title="Click to execute 'ncdump -h' <br> and view metadata"></span> 
				{this.props.file_name}
			</li>
		);
	}
	
});

var AccordionFiles = React.createClass({

	componentDidMount: function(){
		$('.ncdump').tooltip({'placement':'top','html':true,container: 'body'});
	},

	componentDidUpdate: function(){
		$('.ncdump').tooltip({'placement':'top','html':true,container: 'body'});
	},

	render: function(){	
		file_list = [];
		var self = this;
		file_list = this.props.files['data'].map(function(val){
			return <FileItem file_name={val} />
		});
		
		var divStyle = {maxHeight:500, overflow:'auto'};
		return (
			<div className="panel panel-default">
			    <div className="panel-heading">
			      <h4 className="panel-title">
			        <a data-toggle="collapse" href="#collapseFiles">
			        	 Files [{this.props.files['metadata']['numFound']}]
					</a>  
			      </h4>
			    </div>
			
			  	<div id="collapseFiles" className="panel-collapse collapse">
			      <div className="panel-body">
					<div style={divStyle}>
						<ul className="jqueryFileTree">
							{file_list}
						</ul>
				
					</div>
				
			      </div>
			    </div>
			
			  </div>			
		);
	}

});

var AccordionItemList = React.createClass({
	
	render: function(){
		var items=[];
		var self = this;
		$.each(this.props.facets,function(key){
			items.push(<AccordionItem facet_name={key} facet_list={self.props.facets[key]} 
						selected_facets={self.props.selected_facets} updateFacets={self.props.updateFacets}
						key={key}/>);
		});
		return (
			<div className="AccordionItemList panel-group" id="accordion">
				{items}
				<SolrSearchPanel selected_facets={this.props.selected_facets} />
				<AccordionFiles files={this.props.files} />
			</div>
		);
	}
});

var ClearPanel = React.createClass({
	
	render: function(){
		var cx = React.addons.classSet;
		var classes = cx({
			'panel': true,
			'panel-default': true,
			'hidden': Object.keys(this.props.selected_facets).length < 1,
		});
		return (
			<div className="row">
				<div className="col-md-12">
					<div className={classes}>
						<div className="panel-body">
							<a onClick={this.props.clearFacets} href="#">Clear all</a>
						</div>
					</div>
				</div>
			</div>
		);
	}

});

var SolrSearchPanel = React.createClass({
	
	solrSearchCommand: function(){
		solr_list = [];
		$.each(this.props.selected_facets,function(key,val){
			solr_list.push(<span>{key}=<strong>{val}</strong> </span>);
		});
		return solr_list;
	},
	
	render: function(){
		return (
			<div className="panel panel-default">
				<div className="panel-body">
					freva --databrowser {this.solrSearchCommand()}
				</div>
			</div>
		);
	}

});

var DataBrowser = React.createClass({
	getInitialState: function() {
    	return {
      		facets: {},
      		files: {'data':[],'metadata':{'numFound':0}},
      		selected_facets: {},
    	};
  	},

	componentDidMount: function(){
		this.updateFacets();
	},
	
	getQuery: function(){
		result = '';
		$.each(this.state.selected_facets,function(key,val){
			result += '&'+key+'='+val;
		});
		return result;
	},
	
	clearFacets: function(){
		this.replaceState({selected_facets: {}},this.getFacets);
		return false;
	},
	
	updateFacets: function(facet_name,facet_value,clicktype){
		selected_facets = this.state.selected_facets;
		$('#collapse'+facet_name).collapse('hide');
		if(clicktype == 'add')
			selected_facets[facet_name] = facet_value;
		else
			delete selected_facets[facet_name];
		this.replaceState({selected_facets:selected_facets},this.getFacets);
		return false;
	},
	
	getFacets: function(){
		var url = this.props.url + '?facet=*' + this.getQuery();
		var self=this;
		$('html').addClass('wait');
		setTimeout(function(){
			$.ajax(url,{
				async: false,
				dataType: 'json',
				success: function(response){
					files = self.getFiles();
					self.setState({facets:response['data'],files:files});
					$('html').removeClass('wait');
					$('#collapseFiles').collapse('show');
				}
			}); 
		},50);
	},

	getFiles: function(){
		var url = this.props.url + '?start=0&rows=100'+this.getQuery();
		var self=this;
		var result 
		$.ajax(url,{
			async: false,
			dataType: 'json',
			success: function(response){
				result = response;
			}
		});
		return result
	},

	shouldComponentUpdate: function(nextProps, nextState) {
	    if(nextState['facets']){	
			return true
	    }else{
			return false
	    }
	},
	
	render: function(){
		return (
			<div id="dataBrowser">
			    <div className="row">
					<div className="col-md-12">
						<h1>Data-Browser</h1>
					</div>
				</div>
				
				<ClearPanel selected_facets={this.state.selected_facets} clearFacets={this.clearFacets}/>
				
				<div className="row">
					<div className="col-md-12">
						<AccordionItemList updateFacets={this.updateFacets} facets={this.state.facets} 
							selected_facets={this.state.selected_facets} files={this.state.files}/>
					</div>
				</div>
				
				
			</div>
		);
	}

});


