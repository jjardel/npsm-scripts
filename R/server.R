library(shiny)
library( ggplot2 )
library( gridExtra )
library( reshape2 )

# Define server logic for chi-squared application
shinyServer(function(input, output) {

  losvdFrame = read.csv( 'losvds.csv' )
  losvdBins = read.csv( 'binLocations.csv', header = FALSE )
  densityFrame = read.csv( 'densityTable.csv' )

  radii = densityFrame$rk[ 5:1 ]
  topBoundary = array( 0, 5 )
  bottomBoundary = array( 0, 5 )

  minChi = min( densityFrame$chi )

  densParams <- reactive({
    chiLim <- input$deltaChi + minChi
    subset( densityFrame, densityFrame$chi < chiLim )
  })

  
  
  # Reactive expression to generate what I want
  densData <- reactive({
    chiLim <- input$deltaChi + minChi

    #here's where I take $chiLim from input$chiLim

    for( i in 1:5 ){
      topBoundary[ i ] = max( subset( densityFrame$rhok,
                   densityFrame$rk == radii[ i ] & densityFrame$chi < chiLim )
                   )
      bottomBoundary[ i ] = min( subset( densityFrame$rhok,
                      densityFrame$rk == radii[ i ] & densityFrame$chi < chiLim ) ) 
    }
   data.frame( radii, topBoundary, bottomBoundary )
  })

  chiData <- reactive({
    chiLim <- input$deltaChi + minChi
    # now calculate total chi^2 per model by summing across the rows
    losvdFrame$total = rowSums( losvdFrame )

    # subset this to select only models below input chi^2 threshold
    losvdFrameSub = subset( losvdFrame, losvdFrame$total < chiLim )
    
    nRow = length( losvdFrameSub[ ,1 ] )
    nCol = length( losvdFrameSub[ 1, ] ) - 1

    nPoints = nRow * nCol
    r = array( 0, nPoints )
    chi = array( 0, nPoints )

    # total amount of chi^2 in each bin (summed over all models )
    
    chiTotals = colSums( losvdFrameSub )
    normFactor = sum( chiTotals[ 1:nCol ] )
    chiTotals = chiTotals / normFactor * 100

    start = 1
    for( i in 1:nCol ){
      end = start + nRow - 1
      r[ start:end ] = losvdBins[ ,i ]
      chi[ start:end ] = losvdFrameSub[ ,i ]
      start = start + nRow 
    }

    data.frame( r, chi )
  })

  chiTotals <- reactive({
    chiLim <- input$deltaChi + minChi
    # now calculate total chi^2 per model by summing across the rows
    losvdFrame$total = rowSums( losvdFrame )

    # subset this to select only models below input chi^2 threshold
    losvdFrameSub = subset( losvdFrame, losvdFrame$total < chiLim )
    
    nRow = length( losvdFrameSub[ ,1 ] )
    nCol = length( losvdFrameSub[ 1, ] ) - 1

    nPoints = nRow * nCol
    r = array( 0, nPoints )
    chi = array( 0, nPoints )

    # total amount of chi^2 in each bin (summed over all models )
    totals = colSums( losvdFrameSub[ 1:nCol ] )
    normFactor = sum( totals[ 1:nCol ] )
    totals / normFactor * 100
    })

  histoFrame <- reactive({
    chiLim <- input$deltaChi + minChi
    # now calculate total chi^2 per model by summing across the rows
    losvdFrame$total = rowSums( losvdFrame )

    # subset this to select only models below input chi^2 threshold
    losvdFrameSub = subset( losvdFrame, losvdFrame$total < chiLim )
    
    nRow = length( losvdFrameSub[ ,1 ] )
    nCol = length( losvdFrameSub[ 1, ] ) - 1

    losvdFrameSub
  })
      
    
  # Generate a plot of the data.

  # DENSITY PROFILE + CHI^2 PLOT
  output$plot <- renderPlot({
    
    # get density data
    densityProfile = densData()

    # get mean profile
    d1 = log10( densityProfile$bottomBoundary )
    d2 = log10( densityProfile$topBoundary )
    meanDens = 10^rowMeans( cbind( d1, d2 ) )
    
    meanDens.df = data.frame( meanDens, densityProfile$radii )
    names( meanDens.df )[ 2 ] = "radii"

    # get LOSVD data
    chi2.df = chiData()

    
    densPlot = ggplot( densityProfile, aes( x = radii, y = topBoundary ) ) + geom_ribbon( aes( ymax = topBoundary, ymin = bottomBoundary ), alpha = .4 ) + scale_x_log10() + scale_y_log10() + xlab( "R (arcsec)" ) + ylab( expression( rho ) ) + geom_line( data = meanDens.df, aes( x = radii, y = meanDens ) )

    build = ggplot_build( densPlot )
    plotLimits = build$panel$ranges[[1]]$x.range
    xlimits = 10^c( plotLimits[ 1 ], plotLimits[ 2 ] )

    chiPlot = ggplot( chi2.df, aes( x = r, y = chi ) )  + stat_bin2d( bins = 50 ) + scale_x_log10() + scale_fill_continuous( trans = "log", high = "red" ) + theme( legend.position = "none" ) + coord_cartesian( ylim = c( 0, 5 ), xlim = xlimits ) + ylab( expression( chi^2 ) ) + xlab( "R (arcsec)" ) 

    grid.arrange( densPlot, chiPlot, heights = c( 5/8, 3/8 ) )
    
  })

  # PRINT TOTALS
  output$summary <- renderPrint({
    print( chiTotals() )
  })

  # HISTOGRAM PLOT
  output$histo <- renderPlot({
    hist.df = histoFrame()
    hist.df$total = NULL

    nCol = dim( hist.df )[ 2 ]
    plotDim = 1:nCol

    melted = melt( hist.df[ ,plotDim ] )
    
    p = ggplot( melted, aes( value ) ) + geom_histogram( aes( y = ..count.. ), binwidth = 0.05 ) + xlab( expression( chi^2 ) ) + ylab( 'Number of Models' ) + facet_wrap( ~variable, scales = "free" ) 
      print( p )
    
    
  })

#  CAN'T GET THIS WORKING  
#  output$corrplot <- renderPlot({
#    densParams.df = densParams()
#    radii = sort( unique( densParams.df$rk ) )

#    nRow = dim( densParams.df )[ 1 ] / 5
    
    
#    t = subset( densParams.df$model, densParams.df$rk == radii[ 1 ] )
#    newDensFrame = as.data.frame( t )
                                
#    for( i in 1:5 ){
#      tmp = subset( densParams.df$rhok, densParams.df$rk == radii[ i ] )
#      newDensFrame$tmp = tmp
#      names( newDensFrame )[ i + 1 ] = as.character( i )
      
#    }
#    newDensFrame$chi = subset( densParams.df$chi, densParams.df$rk == radii[ 1 ] )
#    p = plotmatrix( newDensFrame[ ,2:6 ], mapping = aes( z = newDensFrame[ ,7 ] ) ) + stat_density2d( aes( z ))


#  })
 
  
})

