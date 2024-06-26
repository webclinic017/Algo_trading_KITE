from kite_trade import *
import pandas as pd
import time
import threading
import multiprocessing
import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import streamlit as st
import asyncio
import pytz

# Set the time zone for the entire script
IST = pytz.timezone('Asia/Kolkata')



class TradingStrategy:
        

        def __init__(self, account, qty, riskpercent,st_instance,message_container):
            self.account = account
            self.qty = qty
            self.percentage = riskpercent
            self.st_instance = st_instance
            self.message_container =message_container
            self.messages = []  # List to store messages
            # self.report_to_streamlit("User Given Percentage",self.percentage)
            



        def fetch_spot_symbols_bn(self,spot_price):
            # ... (unchanged)
            import datetime
            # Get the current date
            current_date = datetime.date.today()

            # Get the current month in text format (e.g., "NOV" for November)
            current_month_text = current_date.strftime('%b')
            current_month = current_date.month
            # print("current month",current_month)

            # Get the current week within the month
            current_week_1 = (current_date.day - 1) // 7 + 1
            day_num = current_date.strftime('%w')
            if ( day_num == '1' or day_num=='0' or day_num=="2" ):
                current_week = 1
            else:
                current_week = 1
            # print("Day:",day_num) 
            # print("Current Week:",current_week) 
            # current_week= 4
            # current_month_text='January'
            # current_month=1
            # current_week=3

            file_path = 'output_banknifty_symbols.csv'
            number_to_match = current_week
            string_to_match = current_month_text

            # List to store extracted strings
            matched_strings = []

            # Open the text file and extract lines based on the criteria
            with open(file_path, 'r') as file:
                for line in file:
                    if str(current_month) in line and str(spot_price) in line:
                        # matched_strings.append(line.strip().split(',')[0])
                        matched_strings.append(line.strip())
                        # print("matched_string",matched_strings)


            sorted_data = sorted(matched_strings, key=lambda s: s.split(',')[1])
            return sorted_data, current_week
        def modify_spotprice(self,input_list, delta):
            # ... (unchanged)
                # Use regular expression to find the last five digits in each string
            modified_list = [re.sub(r'\d{5}(?=[^\d]*$)', lambda x: str(int(x.group()) + delta).zfill(5), string) for string in input_list]
            return modified_list
        def report_to_streamlit(self, message):
        # Use st.text or st.markdown to display messages in Streamlit
            # self.st_instance.text(message)
            self.messages.append(message)  # Append the new message to the list
            self.message_container.text(message)

        def Momentum(self):
            import datetime
            target_time = datetime.time(3, 47, 0)
            target_time2 = datetime.time(11, 59, 0)

            first_phase_start = datetime.time(4,46,0)

            first_phase_end = datetime.time(6,0,0)
            second_phase_start = datetime.time(7,59,0)
            second_phase_end = datetime.time(10,25,0)

            # exit_time= datetime.time(9, 34, 0) ## UK Timings in heroku
            exit_time= datetime.time(23, 34, 0)
            current_time = datetime.datetime.now()
            pt = f" current time is {current_time}"
            self.report_to_streamlit(pt)
            print("Wait for Start")
            while True:
                while (((datetime.datetime.now().time() > first_phase_start) and (datetime.datetime.now().time() < first_phase_end)) or ((datetime.datetime.now().time() > second_phase_start) and (datetime.datetime.now().time() < second_phase_end))):
                    # time.sleep(1)
                    #print("START")

                    while datetime.datetime.now().time() > target_time \
                    and datetime.datetime.now().minute % 1 == 0 \
                    and datetime.datetime.now().second == 1:
                        # Time = datetime.datetime.now()
                        print(datetime.datetime.now())
                        
                        spot = self.account.ltp("NSE:NIFTY BANK")
                        spot_price = spot['NSE:NIFTY BANK']['last_price']
                        spot_price = round(spot_price / 100) * 100

                        spot_symbols_bn_1 = []
                        spot_symbols_bn_1, current_week = self.fetch_spot_symbols_bn(spot_price)
                        spot_symbols_bn_1 = [element.split(',')[0] for element in spot_symbols_bn_1]
                        #print(spot_symbols_bn_1)
                        spot_symbols = spot_symbols_bn_1[current_week * 2 :current_week * 2+2]
                        #print(spot_symbols)
                        trading_symbol_ce = [string for string in spot_symbols if 'CE' in string]
                        trading_symbol_pe = [string for string in spot_symbols if 'PE' in string]
                        st2_trade_symbol_pe = self.modify_spotprice(trading_symbol_pe, 100)
                        st2_trade_symbol_ce = self.modify_spotprice(trading_symbol_ce, -100)

                        previous_price_pe = self.account.ltp("NFO:" + st2_trade_symbol_pe[0])
                        previous_price_pe = previous_price_pe["NFO:" + st2_trade_symbol_pe[0]]['last_price']

                        previous_price_ce = self.account.ltp("NFO:" + st2_trade_symbol_ce[0])
                        previous_price_ce = previous_price_ce["NFO:" + st2_trade_symbol_ce[0]]['last_price']
                        print("PE AND CE PRICE",st2_trade_symbol_pe, previous_price_pe, st2_trade_symbol_ce, previous_price_ce)

                        # time.sleep(57)

                        # current_price_pe = self.account.ltp("NFO:" + st2_trade_symbol_pe[0])
                        # current_price_pe = current_price_pe["NFO:" + st2_trade_symbol_pe[0]]['last_price']

                        # percentage_change = ((current_price_pe - previous_price_pe) / previous_price_pe) * 100

                        waiting_time=0
                        while waiting_time<160:
                            time.sleep(15)
                            current_time = datetime.datetime.now()
                            pt = f" current time is {current_time}"
                            self.report_to_streamlit(pt)

                            current_price_pe = self.account.ltp("NFO:" + st2_trade_symbol_pe[0])
                            current_price_pe = current_price_pe["NFO:" + st2_trade_symbol_pe[0]]['last_price']

                            current_price_ce = self.account.ltp("NFO:" + st2_trade_symbol_ce[0])
                            current_price_ce = current_price_ce["NFO:" + st2_trade_symbol_ce[0]]['last_price']

                            percentage_change_pe = ((current_price_pe - previous_price_pe) / previous_price_pe) * 100
                            percentage_change_ce = ((current_price_ce - previous_price_ce) / previous_price_ce) * 100
                            waiting_time=waiting_time+15
                            if percentage_change_pe >= self.percentage:
                                waiting_time=161
                            elif percentage_change_ce >= self.percentage:
                                waiting_time =161    

                        # print(f"PE: {datetime.datetime.now().time()}, Strike Price: {st2_trade_symbol_pe[0]}, "
                        #                         f"Current_PE_Price: {current_price_pe}, Percentage change in PE: {percentage_change_pe}")
                        # print(f"CE: {datetime.datetime.now().time()}, Strike Price: {st2_trade_symbol_ce[0]}, "
                        #                         f"Current_CE_Price: {current_price_ce}, Percentage change in CE: {percentage_change_ce}")


                        message_pe = f"PE: {datetime.datetime.now().time()}, Strike Price: {st2_trade_symbol_pe[0]}, " \
                                f"Current_PE_Price: {current_price_pe}, Percentage change in PE: {percentage_change_pe}"
                        message_ce = f"CE: {datetime.datetime.now().time()}, Strike Price: {st2_trade_symbol_ce[0]}, " \
                                f"Current_CE_Price: {current_price_ce}, Percentage change in CE: {percentage_change_ce}"
                        print("Percentage change in PE and CE:" , datetime.datetime.now().time(), percentage_change_pe, percentage_change_ce)

                        self.report_to_streamlit(message_pe)
                        self.report_to_streamlit(message_ce)


                        status_message = "Scanning BankNifty options for profitable entries..."
                        status_message += " Please be patient, our AI algorithm is evaluating market conditions."
                        self.report_to_streamlit(status_message)    

                        if percentage_change_pe >= self.percentage:
                            percentage = self.percentage / 100
                            # qty2 = self.qty * 2 if datetime.datetime.now().time() > target_time2 else self.qty

                            order = self.account.place_order(
                                variety=self.account.VARIETY_REGULAR,
                                exchange=self.account.EXCHANGE_NFO,
                                tradingsymbol=st2_trade_symbol_pe[0],
                                transaction_type=self.account.TRANSACTION_TYPE_BUY,
                                quantity=self.qty,
                                product=self.account.PRODUCT_MIS,
                                order_type=self.account.ORDER_TYPE_MARKET
                            )

                            buy_price = self.account.ltp("NFO:" + st2_trade_symbol_pe[0])
                            buy_price = buy_price["NFO:" + st2_trade_symbol_pe[0]]['last_price']
                            print("PE:", datetime.datetime.now().time(), "Traded Price: ", buy_price)
                            # print("PE:", datetime.datetime.now().time(), "Traded Price: ", buy_price,
                            #     "Buy Price :", buy_price, "stoploss PE :",
                            #     (buy_price - 30),
                            #     "Target PE :", (buy_price + 30))
                            message_pe_order = (
                                f"PE: {datetime.datetime.now().time()}, Traded Price: {buy_price}, "\
                                f"Buy Price: {buy_price}, stoploss PE: {buy_price - 30}, "\
                                f"Target PE: {buy_price + 30}"
                            )

                            self.report_to_streamlit(message_pe_order)

                            status_message_pe = " Waiting for right time to exit with happy stoploss or profit.."
                            self.report_to_streamlit(status_message_pe)
                            stop_loss  = buy_price-20
                            target1 = buy_price+12
                            target2 = buy_price+24
                            print("SL,Target1,Target2 PE", stop_loss, target1, target2)

                            while True:
                                current_price = self.account.ltp("NFO:" + st2_trade_symbol_pe[0])
                                current_price = current_price["NFO:" + st2_trade_symbol_pe[0]]['last_price']
                                time.sleep(1)

                                if (stop_loss > current_price) :

                                    order = self.account.place_order(
                                        variety=self.account.VARIETY_REGULAR,
                                        exchange=self.account.EXCHANGE_NFO,
                                        tradingsymbol=st2_trade_symbol_pe[0],
                                        transaction_type=self.account.TRANSACTION_TYPE_SELL,
                                        quantity=self.qty,
                                        product=self.account.PRODUCT_MIS,
                                        order_type=self.account.ORDER_TYPE_MARKET
                                    )
                                    print("PE exited with loss:", datetime.datetime.now().time(), "Exited Price: ", current_price)
                                    message_pe_complete = f" PE tade executed with a loss at $$$$$$,:{current_price}"
                                    self.report_to_streamlit(message_pe_complete)
                                    time.sleep(110)
                                    break 
                                elif ( target1 < current_price) :
                                    qty2 = int((self.qty/2))
                                    order = self.account.place_order(
                                        variety=self.account.VARIETY_REGULAR,
                                        exchange=self.account.EXCHANGE_NFO,
                                        tradingsymbol=st2_trade_symbol_pe[0],
                                        transaction_type=self.account.TRANSACTION_TYPE_SELL,
                                        quantity=qty2,
                                        product=self.account.PRODUCT_MIS,
                                        order_type=self.account.ORDER_TYPE_MARKET
                                    )
                                    print("PE exited first half qty with profit:", datetime.datetime.now().time(), "Exited Price: ", current_price)
                                    while True:                                    
                                        current_price = self.account.ltp("NFO:" + st2_trade_symbol_pe[0])
                                        current_price = current_price["NFO:" + st2_trade_symbol_pe[0]]['last_price']
                                        time.sleep(1)
                                        if buy_price > current_price:                                        
                                            order = self.account.place_order(
                                                variety=self.account.VARIETY_REGULAR,
                                                exchange=self.account.EXCHANGE_NFO,
                                                tradingsymbol=st2_trade_symbol_pe[0],
                                                transaction_type=self.account.TRANSACTION_TYPE_SELL,
                                                quantity=qty2,
                                                product=self.account.PRODUCT_MIS,
                                                order_type=self.account.ORDER_TYPE_MARKET
                                            )
                                            print("PE exited last half qty with profit:", datetime.datetime.now().time(), "Exited Price: ", current_price)
                                            break


                                        elif target2 < current_price:
                                            target1 = target2-10
                                            target2= current_price+20
                                            buy_price = target1
                                            print("Second half qty prices", buy_price, target1, target2 )
                                        
                                    message_pe_complete = f" PE tade executed with Profit at $$$$$$,:{current_price}"
                                    self.report_to_streamlit(message_pe_complete)
                                    time.sleep(110)
                                    break  
                        elif percentage_change_ce >= self.percentage:
                            percentage = self.percentage / 100
                            # qty2 = self.qty * 2 if datetime.datetime.now().time() > target_time2 else self.qty

                            order = self.account.place_order(
                                variety=self.account.VARIETY_REGULAR,
                                exchange=self.account.EXCHANGE_NFO,
                                tradingsymbol=st2_trade_symbol_ce[0],
                                transaction_type=self.account.TRANSACTION_TYPE_BUY,
                                quantity=self.qty,
                                product=self.account.PRODUCT_MIS,
                                order_type=self.account.ORDER_TYPE_MARKET
                            )

                            buy_price = self.account.ltp("NFO:" + st2_trade_symbol_ce[0])
                            buy_price = buy_price["NFO:" + st2_trade_symbol_ce[0]]['last_price']
                            print("CE Buy:", datetime.datetime.now().time(), "Entered Price: ", buy_price)

                            # print("CE:", datetime.datetime.now().time(), "Traded Price: ", buy_price,
                            #     "Buy Price :", buy_price, "stoploss CE :",
                            #     (buy_price - 30),
                            #     "Target CE :", (buy_price + 30))

                            message_ce_order = (
                                f"CE: {datetime.datetime.now().time()}, Traded Price: {buy_price}, "\
                                f"Buy Price: {buy_price}, stoploss CE: {buy_price - 30}, "\
                                f"Target CE: {buy_price + 30}"
                            )

                            self.report_to_streamlit(message_ce_order)

                            stop_loss = buy_price-20
                            target1 = buy_price+12
                            target2 = buy_price+24
                            print("SL,Target1,Target2 CE", stop_loss, target1, target2)

                            status_message_ce = " Waiting for right time to exit with happy stoploss or profit.."
                            self.report_to_streamlit(status_message_ce)

                            while True:
                                current_price = self.account.ltp("NFO:" + st2_trade_symbol_ce[0])
                                current_price = current_price["NFO:" + st2_trade_symbol_ce[0]]['last_price']
                                time.sleep(1)

                                if (stop_loss  > current_price):

                                    order = self.account.place_order(
                                        variety=self.account.VARIETY_REGULAR,
                                        exchange=self.account.EXCHANGE_NFO,
                                        tradingsymbol=st2_trade_symbol_ce[0],
                                        transaction_type=self.account.TRANSACTION_TYPE_SELL,
                                        quantity=self.qty,
                                        product=self.account.PRODUCT_MIS,
                                        order_type=self.account.ORDER_TYPE_MARKET
                                    )
                                    print("CE exited with loss:", datetime.datetime.now().time(), "Exited Price: ", current_price)
                                    message_ce_complete = f" CE tade executed with a LOSS at $$$$$$,:{current_price}"
                                    self.report_to_streamlit(message_ce_complete)
                                    time.sleep(110)

                                    break
                                elif (target1 < current_price):
                                    qty2 = int((self.qty/2))
                                    order = self.account.place_order(
                                        variety=self.account.VARIETY_REGULAR,
                                        exchange=self.account.EXCHANGE_NFO,
                                        tradingsymbol=st2_trade_symbol_ce[0],
                                        transaction_type=self.account.TRANSACTION_TYPE_SELL,
                                        quantity=qty2,
                                        product=self.account.PRODUCT_MIS,
                                        order_type=self.account.ORDER_TYPE_MARKET
                                    )
                                    print("CE exited first half qty with profit:", datetime.datetime.now().time(), "Exited Price: ", current_price)
                                    while True:
                                        
                                        current_price = self.account.ltp("NFO:" + st2_trade_symbol_ce[0])
                                        current_price = current_price["NFO:" + st2_trade_symbol_ce[0]]['last_price']
                                        time.sleep(1)
                                        if buy_price > current_price:
                                            order = self.account.place_order(
                                                variety=self.account.VARIETY_REGULAR,
                                                exchange=self.account.EXCHANGE_NFO,
                                                tradingsymbol=st2_trade_symbol_ce[0],
                                                transaction_type=self.account.TRANSACTION_TYPE_SELL,
                                                quantity=qty2,
                                                product=self.account.PRODUCT_MIS,
                                                order_type=self.account.ORDER_TYPE_MARKET
                                            )
                                            print("CE exited last half qty with profit:", datetime.datetime.now().time(), "Exited Price: ", current_price)
                                            break
                                        elif target2 < current_price:
                                            target1 = target2-10
                                            target2= current_price+20
                                            buy_price = target1
                                            print("Second half qty prices", buy_price, target1, target2 )
                                    
                                    
                                    message_ce_complete = f" CE trade executed with a profit at $$$$$$,:{current_price}"
                                    self.report_to_streamlit(message_ce_complete)
                                    time.sleep(110)
                                    break                                    


            

   
def run_trading_startagies_PE_CE(account_details,quantity,riskpercentage,momentum_trading_enabled,st_instance,message_container):
    kite_accounts = []

    # Initialize KiteConnect instances for each account
    for details in account_details:
        kite = KiteApp(enctoken=details)
        kite_accounts.append(kite)

    strategy_instances = [TradingStrategy(account, riskpercentage, quantity, st_instance,message_container) for account in kite_accounts]

    # Execute the Momentum method for each TradingStrategy instance sequentially
    for strategy_instance in strategy_instances:
        strategy_instance.Momentum()



