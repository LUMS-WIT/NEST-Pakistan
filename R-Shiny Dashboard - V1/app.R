#### Package ####
{
  ## To create shiny dashboard
  library(shinydashboard)
  
  ## Combine JS with shiny
  library(shinyjs)
  
  ## Beautiful UI elements
  library(shinyWidgets)
  
  library(shinyBS)
  
  library(highcharter)
  
  library(shinycssloaders)
  
  library(dplyr)
  
  library(lubridate)

  
  library(tidyverse)

  
  library("lubridate")
  
  
  
}

#################### UI for shiny dashboard  ####################
{
  
  ui <- dashboardPage(skin = "black",
                      
                      dashboardHeader(title = "CO2 Emissions from Pakistan’s Energy sector", titleWidth = "500px"),
                      
                      #### UI Sidebar content  ####
                      {
                        
                        dashboardSidebar(width = "200px",
                                         
                                         ## Enable shiny JS
                                         useShinyjs(),
                                         
                                         br(),
                                         
                                         sidebarMenu(id = 'sidebarMenu',
                                                     menuItem("CO2 Emission", tabName = "tab1")),
                                         
                                         
                                         
                                         # Define side bar skin color and "a" tag color
                                         tags$style(".skin-blue .sidebar a { color: #FFF; }"),
                                         
                                         
                                         
                                         # Define position of shiny notification
                                         tags$style(HTML(".shiny-notification {position:fixed;top: calc(50%);left: calc(50%);}"))
                                         
                        )
                      },
                      
                      
                      ## Body content
                      dashboardBody(
                        
                        # Define statiCard in conditional panel to show output properly when app run first time
                        conditionalPanel("1!=1", statiCard(NULL, NULL, id='HIDDEN'), style="height:0px;margin:0px"),
                        
                        # Enable shiny JS
                        useShinyjs(),
                        
                        
                        tabItems(
                          #### UI Home tab ####
                          tabItem(tabName = "tab1",
                                  
                                  # 1
                                  tabsetPanel(
                                    
                                    tabPanel("Fuel Emissions",
                                             
                                             fluidRow(
                                               ## Pass Input fields Functionality to frontend
                                               
                                               box(solidHeader = FALSE,
                                                   width = 12, collapsible = TRUE, collapsed = FALSE,
                                                   
                                                   ## Pass Input fields Functionality for home tab to frontend
                                                   
                                                   column(12,uiOutput("Fuel"))
                                                
                                                   
                                               ))
                                             
                                             
                                    ),
                                  
                                  # 2
                                    tabPanel("Coal Emissions",
                                             
                                             fluidRow(
                                               ## Pass Input fields Functionality to frontend
                                               
                                               box(solidHeader = FALSE,
                                                   width = 12, collapsible = TRUE, collapsed = FALSE,
                                                   
                                                   ## Pass Input fields Functionality for home tab to frontend
                                                   
                                                   column(12,uiOutput("coal"))
                                                   
                                                   
                                               ))
                                             
                                             
                                    ),
                                
                                  # 3
                                 
                                    tabPanel("Petrolium Emissions",
                                             
                                             fluidRow(
                                               ## Pass Input fields Functionality to frontend
                                               
                                               box(solidHeader = FALSE,
                                                   width = 12, collapsible = TRUE, collapsed = FALSE,
                                                   
                                                   ## Pass Input fields Functionality for home tab to frontend
                                                   
                                                   column(12,uiOutput("Petrolium"))
                                                   
                                                   
                                               ))
                                             
                                             
                                    ),
                                  
                                  # 4
                                    tabPanel("Gas consumption Emissions",
                                             
                                             fluidRow(
                                               ## Pass Input fields Functionality to frontend
                                               
                                               box(solidHeader = FALSE,
                                                   width = 12, collapsible = TRUE, collapsed = FALSE,
                                                   
                                                   ## Pass Input fields Functionality for home tab to frontend
                                                   
                                                   column(12,uiOutput("Gas"))
                                                   
                                                   
                                               ))
                                             
                                             
                                    )
                                    
                                  )
                                  )
                          
                          #### UI History tab ####
                          
                        )
                        
                      )
                      
  )
  
  
}


#################### Server for shiny dashboard  ####################
server <- function(input, output, session) {
  
  
  
  #### Reactive values ####
  {
    RV <- reactiveValues(
      
      data = read.csv("CO2EmissionsfromPakistan’sEnergysector.csv")
      
      
    )
    
    
  }
  
  
  #################### CO2 Emissions  ####################
  
  {
    # 1
    output$Fuel =   renderUI({
      
      data = RV$data
      
      highchart() %>% 
        hc_title(text = "CO2 Emissions by Fuel in Pakistan over past four Decades (Mn Ton)") %>%
        hc_chart(type = "column") %>%
        hc_plotOptions(column = list(stacking = "normal")) %>%
        hc_xAxis(categories = data$Fiscal.Year) %>%
        hc_add_series(name="Oil Emission",
                      data = data$Oil) %>%
        hc_add_series(name="Gas Emission",
                      data = data$Gas) %>%
        hc_add_series(name="Coal Emission",
                      data = data$Coal) %>%
        
        hc_add_series(name="Total Emissions",
                      data = data$Total,
                      type = "line")
      
      
      
    })
    
    # 2
    output$coal =   renderUI({
      
      data = RV$data
      
      highchart() %>% 
        hc_title(text = "Pakistan's Sectoral CO2 emissions from coal consumption by year (Mn Ton)") %>%
        hc_chart(type = "column") %>%
        hc_plotOptions(column = list(stacking = "normal")) %>%
        hc_xAxis(categories = data$Fiscal.Year) %>%
        hc_add_series(name="Household Emission",
                      data = data$Household, color = "orange") %>%
        hc_add_series(name="Power Emission",
                      data = data$Power) %>%
        hc_add_series(name="Bricklin Emission",
                      data = data$Brick.Kilns) %>%
        hc_add_series(name="Cement Emission",
                      data = data$Cement) %>%
        hc_add_series(name="Other Govt",
                      data = data$Other.Govt.) %>%
        
        hc_add_series(name="Total Emissions",
                      data = data$Total.1,
                      type = "line")  
      
      
      
    })
    
    # 3
    output$Petrolium =   renderUI({
      
      data = RV$data
      
      highchart() %>% 
        hc_title(text = "Pakistan's Sectoral CO2 emissions from Petrolium product consumption by year (Mn Ton)") %>%
        hc_chart(type = "column") %>%
        hc_plotOptions(column = list(stacking = "normal")) %>%
        hc_xAxis(categories = data$Fiscal.Year) %>%
        hc_add_series(name="Household Emission",
                      data = data$Household.1, color = "orange") %>%
        hc_add_series(name="Industry Emission",
                      data = data$Industry) %>%
        hc_add_series(name="Agriculture Emission",
                      data = data$Agriculture) %>%
        hc_add_series(name="Transport Emission",
                      data = data$Transport) %>%
        hc_add_series(name="Power Emission",
                      data = data$Power.1) %>%
        hc_add_series(name="Other Govt",
                      data = data$Other.Govt) %>%
        
        hc_add_series(name="Total Emissions",
                      data = data$Total.2,
                      type = "line")  
      
      
    })
    
    # 4
    output$Gas =   renderUI({
      
      data = RV$data
      
      highchart() %>% 
        hc_chart(type = "column") %>%
        hc_title(text = "Pakistan's Sectoral CO2 emissions from Gas consumption by year (Mn Ton)") %>%
        hc_plotOptions(column = list(stacking = "normal")) %>%
        hc_xAxis(categories = data$Fiscal.Year) %>%
        hc_add_series(name="Households Emission",
                      data = data$Households, color = "orange") %>%
        hc_add_series(name="Commercial Emission",
                      data = data$Commercial) %>%
        hc_add_series(name="Cement Emission",
                      data = data$Cement.1) %>%
        hc_add_series(name="Fertilizer Emission",
                      data = data$Fertilizer) %>%
        hc_add_series(name="Power Emission",
                      data = data$Power.2) %>%
        hc_add_series(name="SSGC Emission",
                      data = data$SSGC.) %>%
        hc_add_series(name="Industry Emission",
                      data = data$Industry.1) %>%
        hc_add_series(name="Transport (CNG) Emission",
                      data = data$Transport..CNG...) %>%
        
        hc_add_series(name="Total Emissions",
                      data = data$Total.3,
                      type = "line")  
      
      
      
    })
    
  }
  


}

shinyApp(ui, server)


















