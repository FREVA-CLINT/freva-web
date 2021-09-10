{% load settingstags %}

<script type="text/javascript">

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
"Welcome to the Free Evaluation System Framework (Freva)! Freva is a production system relying on the CMOR data standard, enabling clear data structures and direct access to a multiplicity of consistent data sets.<br><br>You certainly have restricted permissions and not access to all features of this homepage.<br><br>But we invite you to explore the homepage on your own or to follow this guided tour explaining the main features. Enjoy browsing! ",
    placement: "left",
    backdrop: true,


  },
  {
    path: "/plugins/",
    //orphan: true,
    element: "#plugin_menu",
    title: "Tools",
    content: 
    "Here you can access several tools developed within the project. The interfaces of the framework allows unified access to all tools via the command line and the webpage like wise. There is no need to understand the underlying programming languages of the tools and their development environments.",
    placement: "left",
    backdrop: false,
  },
  {
    path: "/plugins/movieplotter/detail/",
    //orphan: true,
    element: "#navigation",
    title: "Movieplotter",
    content:
    "A rather basic example but yet useful example demonstrating the usage of plugins is the movieplotter. The movieplotter creates animations of 2D meteorological datasets.  You can choose if you would like to create a new animation, browse your history with all the previous runs, or look up the documentation. Let&#039;s start a new analysis...",
    placement: "top",
    backdrop: false,
  },
  {
    path: "/plugins/movieplotter/setup/",
    orphan: true,
    //element: "#navigation",
    title: "Movieplotter setup",
    content:
    "You have to set two basic options for selecting the files to be animated. You can either browse the cmor facets, like model and  variable or select your own files from your home or work directory.<br>You'll also be able to change typical plot settings like color bar, plotting range and of course important for an animation the frame rate",
    placement: "top",
    backdrop: false,
  },
  {
    path: "/history/{% settings_val 'GUEST_TOUR_RESULT'%}/results/",
    orphan: true,
    //element: "#history_menu",
    title: "Movieplotter results",
    content: 
    "You are automatically redirected to the result page where you can follow the progress of the submitted movieplotter in “Program's output”. After the tool is finished you can inspect a quickview of the anmiated gif. All results are generally stored in the user&#039;s home or scratch directories, including non-graphically output like netcdf files for further investigations. You can always check the “Configuration” of the tool, to see what has been done and maybe “Edit configuration” to re-run it, for example with a different variable.",
    placement: "left",
    backdrop: true,
  },
  {
    path: "/history/{% settings_val 'GUEST_TOUR_RESULT'%}/results/",
    //orphan: true,
    element: "#sendButton_",
    title: "Share your results",
    content: "You can easily share results of your analysis with colleagues within the project. They recieve an email containing a customizable message and a link to the results.",
    placement: "top",
    backdrop: false,
  },
  {
    path: "/history/{% settings_val 'GUEST_TOUR_RESULT'%}/results/",
    orphan: true,
    //element: "",
    title: "Results from other Users and Plugins",
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
    "The freva system covers one very important part in science: transparency and reproducibilty of the results. For this purpose the evaluation system stores all performed analysis (from command line and web interface) in a common database. So, every analysis can be redone and shared with other scientists easily. The very fast history “Search” enables you to look for specfic analyses you made, by browsing the configurations, which can be viewed by mouse-over on the “info” button.",
    placement: "left",
    backdrop: false,
  },
  {
    path: "/solr/data-browser/",
    orphan: true,
    //element: "",
    title: "Data-Browser",
    content: 
 "Freva offers you direct access to the results to many different datasets stored at DKRZ, like CMIP or CORDEX, and different reanalysis respectively observational data. Due to the huge amount of different data sets there is a clear need for support in finding data. The project integration provides “solr_search” an advanced but easy to use search tool using different standards (CMOR, DRS, CORDEX, etc.). The “Data-Browser” is the web-based pendant to “solr_search”. It enables you to find files or to look up the right CMOR options for the tools.",
    placement: "center",
    backdrop: true,
  },
    {
    path: "/solr/data-browser/",
    orphan: true,
    element: "#variable_search",
    onShow: function(tour){$('#collapsevariable').collapse();$('#variable_search').val('temperature');$('#variable_search').keyup();},
    title: "Data-Browser",
    content: "Still having trouble to understand the variable names in CMOR? Head your mouse over a variable and view the CF-longname for clarification. You can also search for the longname. In this example we are looking for variables containing 'temperature'.",
    placement: "top",
    backdrop: false,
  },
    {
    path: "/solr/data-browser/",
    orphan: true,
    //element: "",
    title: "Data-Browser",
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
    content: "Besides having the contact informations in the footer, the wiki system of the RegiKlim project is used for issue tracking, enabling only one source of reporting. This allows every scientist to track problems with the system or the tools, and maybe don't must ask the same questions answered before.",
    placement: "left",
    backdrop: false,
  },
//  {
//    path: "/wiki",
//    //orphan: true,
//    element: "#wiki_menu",
//    title: "Wiki",
//    content: "All the informations of using&developing the freva system and its tools will be documented in the RegiKlim wiki system. Also you find ways to put your own datasets into the database and standardize it without CMOR.",
//    placement: "left",
//    backdrop: false,
//  },


  {
    path: "/",
    orphan: true,
    //element: "",
    title: "The End",
    content: "Thanks for visting the webpage of the RegIKlim project! For more informations on the scientific tasks of RegiKlim please visit: <a href='https://www.regiklim.de/DE/Home/home_node.html' target='_blank'>RegIKlim Project Side</a><br><br>If you have any question, don't hesitate to write us an email - see footer!<br><br>Have fun!",
    placement: "center",
    backdrop: true,
    template: endTemplate,
  },

]});


function startTour(){
// Initialize the tour
   tour2.init();
   var step = window.localStorage.getItem('tour_current_step');
   if(step !== null )
	setTimeout(function() {tour2.start();},1000);
}

function restartTour(){
   tour2.init();
   // Start the tour
   setTimeout(function() {tour2.restart();},1000);
   //tour.start();}
}

</script>
