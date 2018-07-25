from core import csvfinance_reading as rd, trading as trd
import time
import datetime


def main():
    start_point = datetime.datetime.now()
    # NEED TO BE ENTERED BY USER
    csv_file_path = 'C:/Users/user/PycharmProjects/Strategies_analysing/data_trade_report_moments/'
    csv_file_name = 'msft.csv'
    input_file_data_name = "input_report_dates.txt"
    enter_signal_work_days_before = 1
    exit_signal_work_days_after = 3
    # NEED TO BE ENTERED BY USER

    report_dates = sorted(rd.FinancialDataHelper.read_dates_from_file(csv_file_path + input_file_data_name))
    data_reader = rd.OptionsDataReader(csv_file_path + csv_file_name, 4, 5, 9, 8, 12, 11, 7, True)

    print("work with following input dates:", *report_dates, sep='\n')
    print()
    print("start data reading...", time.asctime())

    data_reader.convert_data_from_file()

    print("data reading complete.", time.asctime())
    print()

    historical_data = data_reader.get_options_data_dict()

    earliest_date = sorted(list(historical_data.keys()))[0]
    latest_date = sorted(list(historical_data.keys()), reverse=True)[0]

    print("earliest/latest dates in historical date file is:", earliest_date, latest_date)
    print()

    deals = []

    for report_date in report_dates:
        if report_date < earliest_date:
            print("date before price history:", report_date)
            print()
            continue

        if report_date > latest_date:
            print("date after price history:", report_date)
            print()
            break

        enter_date = trd.subtract_workdays_from_date(report_date, enter_signal_work_days_before)
        exit_date = trd.add_workdays_to_date(report_date, exit_signal_work_days_after)

        if enter_date < earliest_date or exit_date < earliest_date \
                or enter_date > latest_date or exit_date > latest_date:
            print("deal out of range:", earliest_date, latest_date)
            print()
            continue

        spot_ref = data_reader.get_price_data_by_date(enter_date)
        expiration = trd.get_nearest_friday(exit_date)
        strike = trd.rounding_to_strike_step(spot_ref, trd.define_strike_step(spot_ref))

        if not enter_date in historical_data.keys():
            print("absent in dict:", enter_date)
            continue

        if not exit_date in historical_data.keys():
            print("absent in dict:", exit_date)
            continue

        call_leg_enter = data_reader.get_option_by_args(enter_date, trd.OptionDeal.OPTION_CALL_TYPE, expiration, strike)
        put_leg_enter = data_reader.get_option_by_args(enter_date, trd.OptionDeal.OPTION_PUT_TYPE, expiration, strike)
        call_leg_exit = data_reader.get_option_by_args(exit_date, trd.OptionDeal.OPTION_CALL_TYPE, expiration, strike)
        put_leg_exit = data_reader.get_option_by_args(exit_date, trd.OptionDeal.OPTION_PUT_TYPE, expiration, strike)

        deals.append(create_deal(call_leg_enter, call_leg_exit, 1, trd.Deal.SELL_DEAL_TYPE))
        deals.append(create_deal(put_leg_enter, put_leg_exit, 1, trd.Deal.SELL_DEAL_TYPE))

    temp_counter = 0
    call_put_result = 0.0
    for d in deals:
        print(d)
        call_put_result += d.get_deal_pnl()
        temp_counter += 1
        if temp_counter % 2 == 0:
            print(round(call_put_result, 2))
            print()
            call_put_result = 0.0

    print()
    print('----RESULT-----')
    print("number of deals:", len(deals) / 2)

    res = float(0.0)

    for d in deals:
        res += d.get_deal_pnl()

    print('P&L:', res)
    print()
    print("TIME SPENT:", (datetime.datetime.now() - start_point).seconds, 'sec.')


def create_deal(o_d_r_enter, o_d_r_exit, quantity_abs, deal_type):
    if o_d_r_enter.generate_id() != o_d_r_exit.generate_id():
        raise AttributeError("enter and exit o_d_r have different ID - wrong logic")

    description = str(deal_type + o_d_r_enter.generate_id())

    if deal_type == trd.Deal.BUY_DEAL_TYPE:
        enter_price = o_d_r_enter.ask
        exit_price = o_d_r_exit.bid
    elif deal_type == trd.Deal.SELL_DEAL_TYPE:
        enter_price = o_d_r_enter.bid
        exit_price = o_d_r_exit.ask
        quantity_abs = quantity_abs * -1
    else:
        print("wrong type of deal, have a look at class trading.Deal")
        return None

    return trd.OptionDeal(o_d_r_enter.tradedate, o_d_r_exit.tradedate, enter_price, exit_price,
                          quantity_abs, description, o_d_r_enter.spotref, o_d_r_exit.spotref)


main()
