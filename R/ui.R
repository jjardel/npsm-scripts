library(shiny)

# Define UI for random distribution application 
shinyUI(pageWithSidebar(

  # Application title
  headerPanel("Modeling Results"),

  # Sidebar with controls to select the random distribution type
  # and number of observations to generate. Note the use of the br()
  # element to introduce extra vertical spacing
  sidebarPanel(
    sliderInput("deltaChi", 
                "chi-squared threshold:", 
                 value = 1.0,
                 min = 0.1, 
                 max = 5.84,
                 step = 0.1)
  ),

  # Show a tabset that includes a plot, summary, and table view
  # of the generated distribution
  mainPanel(
      tabsetPanel( 
                  tabPanel( "Plot", plotOutput("plot"),
                           h4( "Percentage of total contribution to chi-squared" ),
                           verbatimTextOutput( "summary" ) ),
                  tabPanel( "Correlations",plotOutput( "corrplot" ) ),
                  tabPanel( "1-D Histograms", plotOutput( "histo" ) ) ) )
))

