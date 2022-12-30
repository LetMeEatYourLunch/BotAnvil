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
library(fst)
library(reticulate)


# Inits -------------------------------------------------------------------

#tags$style("@import url(https://use.fontawesome.com/releases/v5.7.2/css/all.css);")
#Sys.setenv(RETICULATE_PYTHON = "C:/ProgramData/Anaconda3")

#repl_python()
source_python("C:/Users/user/Documents/Python Scripts/Projects/TraderTool/analyse_tickers.py")


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
                                           , box(DTOutput("available_ticker")
                                                 , width = 12
                                                 , height = "40vh")
                                           , box(DTOutput("selected_stocks")
                                                 , width = 12
                                                 , height = "40vh")
                                           )

                                    )
                                  , fluidRow(
                                    column(actionBttn("pulldata_btn"
                                                      , label = "Pull data"
                                                      , style = "pill"
                                                      , color = "primary"
                                                      , size = "lg"
                                                      , block = FALSE
                                                      , no_outline = TRUE)
                                           , width = 12
                                           , align = "right"))
                                  )
                          
                          , tabItem(tabName = "charts"
                                    , fluidRow(
                                      column(width = 12
                                             , box(uiOutput("ticker_picker_radio")
                                                   , width = 12
                                                   , height = "40vh")
                                             , box(echarts4rOutput("candle_stick_plt")
                                                   , width = 12
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
  
  # Import python back-end for pipeline
  source_python("C:/Users/user/Documents/Python Scripts/Projects/TraderTool/analyse_tickers.py")
  # Get meta data; list of available stocks on ASX for user to choose from
  # TODO: reference a yaml
  setwd("C:/Users/user/Documents/Python Scripts/Projects/TraderTool/")
  # TODO: reference yaml
  asx_ticker_dt <- data.table(fread("ASX_Listed_Companies_23-12-2022_06-47-11_AEDT.csv"))
  # Set column names
  setnames(asx_ticker_dt, "ASX code", "TICKER")
  setnames(asx_ticker_dt, "Company name", "NAME")
  setnames(asx_ticker_dt, "Listing date", "LIST_DT")
  setnames(asx_ticker_dt, "GICs industry group", "SECTOR")
  setnames(asx_ticker_dt, "Market Cap", "CAP")
  # Add index col, for filtering.
  asx_ticker_dt[["ID"]] <- base::seq.int(nrow(asx_ticker_dt))


# Get stock selection from User -------------------------------------------

  output$available_ticker <- renderDT({
    asx_ticker_dt %>%
      # Hide unnecesarry data from user
      datatable(rownames = FALSE
                , options = list(columnDefs = list(list(visible = FALSE
                                                        , targets=c("ID"
                                                                    , "CAP"
                                                                    , "LIST_DT")))))
  })
  # Dynamically (Reactive data) filter using Client data (user input) 
  reactive_asx_ticker_data <- reactive({
    req(input$available_ticker_rows_selected)
    asx_ticker_dt %>%
      filter(`ID` %in% input$available_ticker_rows_selected)
  })
  # Render the filtered data so User can verfiy their selection
  output$selected_stocks <- renderDT({
    reactive_asx_ticker_data() %>%
      # Hide unnecesarry data from user
      datatable(rownames = FALSE
                , options = list(paging = FALSE
                                 , searching = FALSE
                                 , scrollY = "30vh"
                                 , scrollX = "100%"
                                 , columnDefs = list(list(visible = FALSE
                                                         , targets=c("ID")))))
  })
  
  

# Pull time series from asx -----------------------------------------------
  # Listen to pull data event
  observeEvent(input$pulldata_btn, {
    showNotification("Retrieving data")
    # Get selected tickers
    sel_tickers <- reactive_asx_ticker_data()
    if (length(sel_tickers) > 0) {
      
      sel_tickers_unq <- unique(sel_tickers$TICKER)
      
      if (length(sel_tickers_unq) == 1){
        sel_tickers_unq <- list(sel_tickers_unq)
      }
      # Pull data from asx

      ts_raw <- analyse_tickers(sel_tickers_unq)
      # Data sanitation; convert volume from list to array; if needed
      if (typeof(ts_raw$volume) == "list") {
        
        ts_raw[["volume"]] <- unlist(ts_raw[["volume"]])
        
      }
      # Data sanitisation; convert close_date (Unix time) to lubridate datetime
      ts_raw[["close_date"]] <- lubridate::as_datetime(ts_raw[["close_date"]])
      
      fst::write.fst(as.data.frame(ts_raw), "asx_time_series.fst")
      
    } else {
      
      showNotification("Warning: No stocks selected")
      
    }
    # Regenerate radio button options for single stock selection now that 
    # selected stocks have changed
    
    # Restrict user choice to a single stock from stock data they have pulled
    output$ticker_picker_radio <- renderUI({
      
      
      if (isTRUE(file.exists("asx_time_series.fst"))) {
        
        ts_raw <- fst::read.fst("asx_time_series.fst", as.data.table = TRUE)
        
        choices <- list()
        for (code in unique(ts_raw$code)) {
          
          choices[[code]] <- code
          
        }
        
      } else {
        
        choices <- c("")
        
      }
      
      radioButtons("ticker_picker_radio"
                   , label = h3("Select Stock: ")
                   , choices = choices
                   , selected = 1)
      
    })
    plotter(input, output)
    

  })
  
  # Restrict user choice to a single stock from stock data they have pulled
  output$ticker_picker_radio <- renderUI({
    
    
    if (isTRUE(file.exists("asx_time_series.fst"))) {
      
      ts_raw <- fst::read.fst("asx_time_series.fst", as.data.table = TRUE)
      
      choices <- list()
      for (code in unique(ts_raw$code)) {
        
        choices[[code]] <- code
        
      }
      
    } else {
      
      choices <- c("")
      
    }
    
    radioButtons("ticker_picker_radio"
                 , label = h3("Select Stock: ")
                 , choices = choices
                 , selected = 1)
    
  })
 

  
plotter <- function(input, output) {
  
  output$candle_stick_plt <- renderEcharts4r({
    # Does file exist and has a stock been chosen?
    if (isTRUE(file.exists("asx_time_series.fst"))) {
      
      ts_raw <- fst::read.fst("asx_time_series.fst", as.data.table = TRUE)
      # Open price is previous day's close price
      ts_raw[, open_price := shift(close_price
                                   , n = 1
                                   , type = "lag")
             , by = "code"]
      # Slice by selected code
      if (!is.null(input$ticker_picker_radio)) {
        ts_raw_code <- ts_raw[code == input$ticker_picker_radio]
      } else {
        default_code <- unique(ts_raw$code)[1]
        ts_raw_code <- ts_raw[code == default_code]
      }
      # Convert date to format readible by echarts4r (drop time of day)
      ts_raw_code[, date := format(as.Date(close_date), "%Y-%m-%d")]
      ts_raw_code <- ts_raw_code[order(date)]
      # Echarts 4r needs data.frame
      ts_raw_code = as.data.frame(ts_raw_code)
      # set index column to date (so that echarts4r displays time correctly)
      rownames(ts_raw_code) <- ts_raw_code[["date"]]
      ts_raw_code |>
        e_charts(date) |>
        e_candle(open_price
                 , close_price
                 , day_low_price
                 , day_high_price
                 , name = input$ticker_picker_radio) |>
        e_datazoom(type = "slider") |>
        e_title("Candlestick chart", input$ticker_picker_radio)
      
    } else {
      warning(paste0("File not found: "
                     , "asx_time_series.fst"
                     , ". Stocks may not have been selected"))
    }
    
    
    
  })
}
  
}

# Run the application 
shinyApp(ui = ui, server = server)

