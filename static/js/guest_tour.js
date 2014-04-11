var tourTemplate = "<div class='popover tour ' ><div class='arrow'></div><button class='close' aria-hidden='true' data-dismiss='modal' type='button' data-role='end' style='margin-right:10px;margin-top:5px;'>X</button><h3 class='popover-title'></h3><div class='popover-content' ></div><div class='popover-navigation'><button class='btn btn-default tourbtn' data-role='prev'>< Back</button><button class='btn btn-default tourbtn' data-role='next'>Next ></button></div></div>";

var endTemplate = "<div class='popover tour'><div class='arrow'></div><button class='close' aria-hidden='true' data-dismiss='modal' type='button' data-role='end' style='margin-right:10px;margin-top:5px;'>X</button><h3 class='popover-title'></h3><div class='popover-content'></div><div class='popover-navigation'><button class='btn btn-default' data-role='prev'>< Back</button><button class='btn btn-default' data-role='end'>End Tour </button></div></div>";

// Instance the tour
var tour2 = new Tour({
  template:tourTemplate,
  steps: [
  {
    path: "/",
    orphan: true,
    //element: "#maincontent",
    title: "Guest login",
   content: 
"Dear Guest,<br><br>welcome to the MiKlip homepage of the decadal climate prediction and evaluation system! It is a production system relying on the CMIP5 data standards, enabling clear data structures and direct access to a multiplicity of consistent data sets.<br><br>You certainly have restricted permissions and not access to all features of this homepage.<br><br>But we invite you to explore the homepage on your own or to follow this guided tour explaining the main features. Enjoy browsing! ",
    placement: "left",
    backdrop: true,


  },
  {
    path: "/plugins/",
    //orphan: true,
    element: "#plugin_menu",
    title: "Tools",
    content: 
    "Here you can access several tools developed within the MiKlip project. The project INTEGRATION provides a standardized framework for tool development. The interfaces of the framework allow a unified access to the tools from the shell and the webpage, as well. There is no need to understand the programming languages underlying the tools and their development environments.",
    placement: "left",
    backdrop: false,
  },
  {
    path: "/plugins/murcss/detail/",
    //orphan: true,
    element: "#navigation",
    title: "MurCSS",
    content:
    "One tool for the evaluation of decadal climate predictions is the MurCSS plugin. It offers the user verification methods following the decadal evaluation framework suggested by Goddard et al. (2013). Here you can choose if you would like to start an analysis, browse your history with all the tool runs, or look up the documentation. Let&#039;s start an analysis...",
    placement: "top",
    backdrop: false,
  },
  {
    path: "/plugins/murcss/setup/",
    orphan: true,
    //element: "#navigation",
    title: "MurCSS setup",
    content: 
    "To start an analysis with MurCSS, you have to set several options. Some options are very specific for a single tool like the lead times for decadel analysis. For generic options, like output directories which are included in almost any tool, the webpage offers standardized selection methods. Here, we would like to point out the selection of the input files. Instead of giving the path to some input directories or collecting all datasets, you only have to specify the CMOR options of the experiments you want to evaluate. The built-in search framework supports you to find the data you need by giving possible suggestions, e.g. variables to be choosen. The setup checks possibilities even for the observational or reanalysis data sets to be compared to.<br><br>All tools run on a high performance computer enabling a fast evaluation. Let&#039;s have look at the results.",
    placement: "top",
    backdrop: false,
  },
  {
    path: "/history/4841/results/",
    orphan: true,
    //element: "#history_menu",
    title: "MurCSS results",
    content: 
    "You are automatically redirected to the result page of your analysis where you can follow the progress of the submitted evaluation in “Program's output”. After the tool is finished you can browse the results in the quickview section “Results”. All results are generally stored in the user&#039;s home or scratch directories, including non-graphically output like netcdf files for further investigations. You can always check the “Configuration” of the analysis, to see what has been done and maybe “Edit configuration” to re-run it, for example with a different observational dataset.",
    placement: "left",
    backdrop: true,
  },
  {
    path: "/history/4841/results/",
    //orphan: true,
    element: "#sendButton_",
    title: "Share your results",
    content: "You can easily share results of your analysis with colleagues in the MiKlip project. They recieve an email containing a customizable message and a link to the results.",
    placement: "top",
    backdrop: false,
  },
  {
    path: "/history/4841/results/",
    orphan: true,
    //element: "",
    title: "MurCSS results",
    content: "Feel free to browse the results.",
    placement: "center",
    backdrop: false,
  },

  {
    path: "/history/",
    //orphan: true,
    element: "#history_menu",
    title: "History",
    content: 
    "The evaluation system covers one very important part in climate science: transparency and reproducibilty of the results. For this purpose the evaluation system stores all performed analysis (from command line and web interface) in a common database. So, every analysis can be redone and shared with other scientists easily. The very fast history “Search” enables you to look for specfic analyses you made, by browsing the configurations, which can be viewed by mouse-over on the “info” button.",
    placement: "left",
    backdrop: false,
  },
  {
    path: "/solr/data-browser/",
    orphan: true,
    //element: "",
    title: "Data-Browser",
    content: 
 "The system offers you direct access to the results of the MiKlip prediction system (baseline0, baseline1, prototype), the CMIP5 ESGF data-node of the DKRZ, and different reanalysis respectively observational data. Due to the huge amount of different data sets there is a clear need for support in finding data. The project INTEGRATION provides “solr_search” an advanced but easy2use search tool using different standards (CMOR, DRS, CORDEX, etc.). The “Data-Browser” is the web-based pendant to “solr_search”. It enables you to find files or to look up the right CMOR options for the tools.<br>Still having trouble to understand the variable names in CMOR? Head your mouse over a variable and view the CF-longname for clarification.",
    placement: "center",
    backdrop: true,
  },
    {
    path: "/solr/data-browser/",
    orphan: true,
    //element: "",
    title: "MurCSS results",
    content: "Feel free to browse the data.",
    placement: "center",
    backdrop: false,
  },

  {
    path: "/plugins/about/",
    //orphan: true,
    element: "#docu_menu",
    title: "Documentation",
    content: 
    "The documentation area is still under development, using web versions of, for example latex, to access informations directly from the tool on the hpc-system. This ensures one common way of providing documentations of tools for the shell and web version.",
    placement: "left",
    backdrop: false,
  },
  {
    path: "/contact/",
    //orphan: true,
    element: "#contact_menu",
    title: "Contact",
    content: "Beside having the contact informations in the footer, the wiki system of the MiKlip project is used for issue tracking, enabling only one source of reporting. This allows every scientist to track problems with the system or the tools, and maybe don't must ask the same questions answered before.",
    placement: "left",
    backdrop: false,
  },
  {
    path: "/wiki",
    //orphan: true,
    element: "#wiki_menu",
    title: "Wiki",
    content: "All the informations of using&developing the evaluation system and its tools are documented in the MiKlip wiki system. Also you find ways to put your own datasets into the database and standardize it without CMOR.",
    placement: "left",
    backdrop: false,
  },


  {
    path: "/",
    orphan: true,
    //element: "",
    title: "The End",
    content: "Thanks for visting the webpage of the MiKlip project! For more informations on the scientific tasks of MiKlip please visit: <a href='http://www.fona-miklip.de' target='_blank'>www.fona-miklip.de</a><br><br>If you have any question, don't hesitate to write us an email - see footer!<br><br>Have fun!",
    placement: "center",
    backdrop: true,
    template: endTemplate,
  },

]});


function startTour(){
// Initialize the tour
   tour2.init();
   var step = window.localStorage.getItem('tour_current_step');
   console.log(step);
   if(step !== null )
	setTimeout(function() {tour2.start();},1000);
}

function restartTour(){
   tour2.init();
   // Start the tour
   setTimeout(function() {tour2.restart();},1000);
   //tour.start();}
}

