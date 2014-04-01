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
    content: "Dear Guest,<br><br>welcome to the MiKlip homepage of the decadal climate prediction and evaluation system! It is a production system relying on the CMIP5 data standards, enabling clear data structures and direct access to a multiplicity of consistent data sets.<br><br>You certainly have restricted permissions and not access to all features of this homepage.<br><br>But we invite you to explore the homepage and the evaluation system. Enjoy the browsing! ",
    placement: "left",
    backdrop: true,
  },
  {
    path: "/plugins/",
    //orphan: true,
    element: "#plugin_menu",
    title: "Tools",
    content: "Here you find several tools developed within the MiKlip project. The project INTEGRATION provides a standardized framework for tool development. It enables an user-friendly and consistent way of using several software packages, without any need to understand different programming languages. The plugin management allows software developers to stay in their familiar code environment and benefit from the instantaneous appearance in the command-line and web system.",
    placement: "left",
    backdrop: false,
  },
  {
    path: "/plugins/murcss/detail/",
    //orphan: true,
    element: "#navigation",
    title: "MurCSS",
    content: "One tool for evaluating decadal climate prediction is the MurCSS plugin. It enables the MiKlip project verification methods following the decadal evaluation framework suggested by Goddard et al. (2013). Here you could start an analysis, show your history with the tool and look up the documentation. Let's start an analysis...",
    placement: "top",
    backdrop: false,
  },
  {
    path: "/plugins/murcss/setup/",
    orphan: true,
    //element: "#navigation",
    title: "MurCSS setup",
    content: "For starting an analysis like MurCSS, you have to choose some standard options like output directories or some specific options like the leadtimes for decadal analysis. Instead of pointing to some input directories or collecting all datasets, you only have to specify the CMOR options of the experiments you want to evaluate. The inbuild search framwork helps the users to find the data they need, by giving possible suggestions like e.g. variables to be choosen. The setup checks possibilities even for the observational or reanalysis data sets to be compared to.<br><br>All tools running on a high performance computer enables a fast evaluation. Lets have look the results.",
    placement: "top",
    backdrop: false,
  },
  {
    path: "/history/3966/results/",
    orphan: true,
    //element: "#history_menu",
    title: "MurCSS results",
    content: "You automatically land on the result page of your analysis where you can follow the progress of that evaluation in “Program's output”. After the tool is finished you can check the “Results” by browsing through the quickview section. All results are generally stored in the users home or scratch directories, including non-graphically output like netcdf files for further investigations. You can always check the “Configuration” of the analysis, to see what has been done and maybe “Edit configuration” to rerun it with for example an other observational dataset.",
    placement: "left",
    backdrop: true,
  },
  {
    path: "/history/3966/results/",
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
    content: "For the very important part in climate science of transparency and reproducibilty, all analyses made with the evaluation system including the command-line version are saved in a database, can be redone and shared with other scientists. The very fast history “Search” enables to look for specfic analyses you made, by browsing the configurations, which can be viewed on-mouse over the “info” button.",
    placement: "left",
    backdrop: false,
  },
  {
    path: "/solr/data-browser/",
    orphan: true,
    //element: "",
    title: "Data-Browser",
    content: "With direct access to the MiKlip prediction system results (baseline0,baseline1,prototype) and the CMIP5 ESGF data-node of the DKRZ, different reanalyses and observational datasets, there is a clear need for support in finding the data. The project INTEGRATION provides “solr_search” an advanced but easy2use search tool, using different standards (CMOR, DRS, CORDEX, etc). The “Data-Browser” enables this search tool in the web for looking up files, its directories or maybe just the right CMOR options for the “Tools”. Still having trouble to understand the variable names in CMOR? Head your mouse over a variable and view the CF-longname for clarification.",
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
    content: "The documentation area is still under development, using web versions of, for example latex, to access informations directly from the tool on the hpc-system. This ensures one common way of providing documentations of tools and administrating not a shell and a webversion.",
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
    content: "Thanks for visting the webpage of the MiKlip project! For more informations on the scientific tasks of MiKlip please visit: <a href='http://www.fona-miklip.de' target='_blank'>www.fona-miklip.de</a><br><br>If you have any question, don't hesitate to write us an email - see footer!<br><br>Good Bye",
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

