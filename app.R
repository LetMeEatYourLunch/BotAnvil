#
# This is a Shiny web application. You can run the application by clicking
# the 'Run App' button above.
#
# Find out more about building applications with Shiny here:
#
#    http://shiny.rstudio.com/
#

library(shiny)
library(shinydashboard)
library(DT)
library(echarts4r)
library(leaflet)
library(shinyWidgets)
library(googlesheets4)
library(data.table)
library(dplyr)
library(scales)


# Inits -------------------------------------------------------------------

#tags$style("@import url(https://use.fontawesome.com/releases/v5.7.2/css/all.css);")


# Define UI for application that draws a histogram
ui <- dashboardPage(skin = 'black'
                    , dashboardHeader( title = "Bot Anvil")
                    , dashboardSidebar(
                      sidebarMenu(
                        menuItem(tabName = "portfolio"
                                 , text = "Portfolio"
                                 , icon = icon("folder-open")
                        )
                        , menuItem(tabName = "charts"
                                   , text = "Charts"
                                   , icon = icon("folder-open")
                                   
                        )
                        , menuItem(tabName = "results"
                                   , text = "Results"
                                   , icon = icon("chart-bar")
                        )
                      )
                    )
                    , dashboardBody(
                      fillPage(
                        tabItems(
                          tabItem(tabName = "portfolio"
                                  , fluidRow(
                                    column(width = 12
                                           , box(uiOutput("ticker_picker")
                                                 , width = 12
                                                 , height = "40vh")
                                           , box(DTOutput("selected_stocks")
                                                 , width = 12
                                                 , height = "40vh")
                                    )
                                  )
                          )
                          , tabItem(tabName = "item-dc"
                                    , fluidRow(
                                      column(width = 12
                                             , box(width = 12
                                                   , height = "40vh"
                                                   , DTOutput("item_dc_tbl"))
                                      )
                                    )
                          )
                          , tabItem(tabName = "summary"
                                    , fluidRow(
                                      column(width = 6
                                             , box(width = 6
                                                   , height = "40vh")
                                             , box(width = 6
                                                   , height = "40vh")
                                      )
                                    )
                          )
                        )
                      )
                    )
)


# Define server logic required to draw a histogram
server <- function(input, output) {
  
  # Get data ----------------------------------------------------------------
  setwd("C:/Users/user/Documents/Python Scripts/Projects/TraderTool/")
  asx_ticker_dt <- data.table(fread("ASX_Listed_Companies_23-12-2022_06-47-11_AEDT.csv"))
  setnames(asx_ticker_dt, "ASX code", "TICKER")
  setnames(asx_ticker_dt, "Company name", "NAME")
  setnames(asx_ticker_dt, "Listing date", "LIST_DT")
  setnames(asx_ticker_dt, "GICs industry group", "SECTOR")
  setnames(asx_ticker_dt, "Market Cap", "CAP")
  

  # Filter ------------------------------------------------------------------
  output$ticker_picker <- renderUI({
    choices <- unique(asx_ticker_dt[["TICKER"]])
    pickerInput("ticker_picker"
                , "Select stock"
                , multiple = TRUE
                , choices = choices)
  })
  

  
  # Reactive data -----------------------------------------------------------
  reactive_asx_ticker_data <- reactive({
    req(input$ticker_picker)
    asx_ticker_dt %>%
      filter(`TICKER` == input$ticker_picker)
             #, Category %in% input$category_check_box)
  })
  
  output$selected_stocks <- renderDT({
    reactive_asx_ticker_data() %>%
      datatable(rownames = FALSE
                , options = list(paging = FALSE
                                 , scrollY = "30vh"
                                 , scrollX = "100%"))
  })
  
  
  
  
}

# Run the application 
shinyApp(ui = ui, server = server)

