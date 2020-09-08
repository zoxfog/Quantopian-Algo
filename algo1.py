import quantopian.algorithm as algo
from quantopian.pipeline import CustomFactor, Pipeline
from quantopian.pipeline.data.builtin import USEquityPricing
from quantopian.pipeline.factors import SimpleMovingAverage, AverageDollarVolume
from quantopian.pipeline.data import morningstar,Fundamentals
from quantopian.pipeline.classifiers.fundamentals import Sector
from quantopian.algorithm import order_optimal_portfolio
import pandas
import numpy
import quantopian.optimize as opt
from quantopian.pipeline.filters.fundamentals import IsPrimaryShare
from quantopian.pipeline.filters import QTradableStocksUS


#This class computes the standard deviation
class StdDev(CustomFactor):
    def compute(self, today, asset_ids, out, values):
        # Calculates the column-wise standard deviation, ignoring NaNs
        out[:] = numpy.nanstd(values, axis=0)#nan to ignore NaN
        
#This class gets the yearly high
class High252(CustomFactor):  
    window_length = 252 # ~52 weeks  
    inputs = [USEquityPricing.high]  
    def compute(self, today, asset_ids, out, high_prices):  
        out[:] = numpy.max(high_prices, axis=0)
        
#This class gets the 3 month high        
class High66(CustomFactor):  
    window_length = 252 # ~52 weeks  
    inputs = [USEquityPricing.high]  
    def compute(self, today, asset_ids, out,high_prices ):  
        out[:] = numpy.max(high_prices, axis=0)
        
#This class gets the yearly low
class Low252(CustomFactor):  
    window_length = 252 # ~52 weeks  
    inputs = [USEquityPricing.low]  
    def compute(self, today, asset_ids, out, low_prices):  
        out[:] = numpy.min(low_prices, axis=0)  
        
def initialize(context):
    
    schedule_function(my_rebalance, date_rules.week_start(), time_rules.market_open( minutes=5))
    
    #Create the Pipleline
    my_pipe = make_pipeline()
    
    #Attach the pipelione to my workspace
    algo.attach_pipeline(my_pipe, 'my_pipeline')  
    

def my_rebalance(context, data):
    


    #sell the position in the portfolio
    for security in context.portfolio.positions:
        if security not in context.valid_open_position and data.can_trade(security):
            order_target_percent(security,0)
            
    #add a poisition to the portfolio       
    for security in context.longs:
        if data.can_trade(security):
            order_target_percent(security, context.long_weight)

def my_compute_weights(context):
    
    #allocate 0.5/(the number of long stocks) of the portfolio's value for each 'long' security in the pipeline
    long_weight = 0.5/len(context.longs)
    
    return (long_weight)


def before_trading_start(context, data):
    
    #create a custom df with the pipline's data
    context.jellyfish =algo.pipeline_output('my_pipeline')
    
    # create a list of securities that we intend going long on
    context.longs = context.jellyfish[context.jellyfish['longs']==1].sort_values(by=['rv'],ascending=False).head(15).index.tolist()
    
    context.valid_open_position = context.jellyfish[context.jellyfish['valid_open_position']==1].index.tolist()
    
    context.long_weight = my_compute_weights(context)
    
    print(context.long_weight)
    print(context.longs)
    #print( context.account)
    
    

def make_pipeline():

    base_universe = QTradableStocksUS()
    
    latest_close = USEquityPricing.close.latest  
    latest_volume = USEquityPricing.volume.latest
    latest_close = USEquityPricing.close.latest
    mkt_cap = morningstar.valuation.market_cap.latest
    symbol_float1 = morningstar.Fundamentals.shares_outstanding.latest
    symbol_float2 = morningstar.Fundamentals.ordinary_shares_number.latest
    morningstar_sector = Sector()
    
    volume_3_months = AverageDollarVolume(
    window_length = 66,
    mask =base_universe  & (mkt_cap<5000000000) #masking 
    )
        
    volume_1_day = AverageDollarVolume(
    window_length = 1,
    mask =base_universe & (mkt_cap<5000000000) #masking 
    )
    
    mean_close_30 = SimpleMovingAverage(
    inputs=[USEquityPricing.close],
    window_length=30,
    mask = base_universe & (mkt_cap<5000000000) #masking
    )
    
    
    rv = volume_1_day/volume_3_months
    
    high_52_w = High252()
    high_3_m = High66()
    low_52_w = Low252()


    # price at 30%, 50%, 60% and 90% respectively of the yearly price range
    third_range = (high_52_w-low_52_w)*(1/3) + low_52_w
    half_range = (high_52_w-low_52_w)*0.5 + low_52_w
    sixty_range = (high_52_w-low_52_w)*0.6 + low_52_w
    ninty_range = (high_52_w-low_52_w)*0.9 + low_52_w
    fifteen_range = (high_52_w-low_52_w)*0.15 + low_52_w
    
    #create the price range for potential longs
    long_range = (latest_close<=sixty_range) & (latest_close>=third_range)
    
    #take profit range
    tp_range = latest_close>=ninty_range
    
    #stop loss range
    sl_range = latest_close<=fifteen_range
  
    valid_open_position_range = (latest_close<=ninty_range) & (latest_close>=fifteen_range)

    #filters (the data type is a zipline pipeline filter not a df)
    # returns True or False per row (per symbol):
    close_price_filter = (latest_close < 15) 
    price_under_30mva = latest_close < mean_close_30 #price under 30 mva
    
    
    #create a list of stocks for potential longs
    universe =  close_price_filter & base_universe & (mkt_cap<5000000000)
    
    # create the "go long" critera
    longs = price_under_30mva & long_range
 
    
    return Pipeline(
        columns={
            'latest_close': latest_close,
            'rv': rv,
            'stop_loss': sl_range,
            'take_profit': tp_range,
            'valid_open_position':valid_open_position_range,
            'longs': longs 
        },
        screen=universe
    )