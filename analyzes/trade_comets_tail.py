from core import csvfinance_reading as rd
from core import trading as trd
import time


def main():
    # NEED TO BE ENTERED BY USER
    #
    # THIS INPUTS WILL BE USED TO FIND TRADE POINTS
    csv_file_path = 'C:/Users/user/PycharmProjects/Strategies_analysing/data_trade_comets_tail/'
    csv_file__price_name = 'prices.csv'
    csv_file_implvol_name = 'implvols.csv'
    csv_file_option_name = 'options.csv'
    date_format = "%d.%m.%Y"
    delimiter = ';'

    iv_entropy_period_days = 30
    iv_calm_period_days = 15
    iv_entropy_value = 0.6
    iv_calm_value = 0.2
    price_drop_enough_value = 0.03
    # ------------------------------------------------------------------------
    #
    # THIS INPUTS WILL BE USED MAKE DEALS WITH OPTION, USING TRADE POINTS (ABOVE)
    days_to_expiration = 30
    spot_strike_steps = 0
    option_type = trd.OptionDeal.OPTION_PUT_TYPE
    # ------------------------------------------------------------------------

    print("start data reading...", time.asctime())

    price_reader = rd.HistoricalDataReader(csv_file_path + csv_file__price_name, file_date_format=date_format)
    vol_reader = rd.HistoricalDataReader(csv_file_path + csv_file_implvol_name, file_date_format=date_format)
    option_reader = rd.OptionsDataReader(csv_file_path + csv_file_option_name, 4, 5, 9, 8, 12, 11, 7, True)

    price_reader.convert_data_from_file(delimiter=delimiter)
    print("price data read", time.asctime())
    vol_reader.convert_data_from_file(delimiter=delimiter)
    print('IV data read', time.asctime())
    option_reader.convert_data_from_file()
    print("options data read", time.asctime())

    print("data reading complete.", time.asctime())

    ticker = vol_reader.get_tickers_list()[0]

    trades_for_deal = lookup_for_trading_dates(price_reader.get_historical_data_dict()[ticker],
                                               vol_reader.get_historical_data_dict()[ticker],
                                               iv_entropy_value,
                                               iv_calm_value,
                                               iv_entropy_period_days,
                                               iv_calm_period_days,
                                               price_drop_enough_value)

    print('potential trades number:', len(trades_for_deal))
    for date in trades_for_deal:
        print(rd.FinancialDataHelper.convert_date_to_str(date, "%d.%m.%Y"))

    print()
    print()

    print("start to make trades...", time.asctime())


def lookup_for_trading_dates(price_quotes, iv_quotes, iv_entropy_value, iv_calm_value, iv_entropy_period,
                             iv_calm_period,
                             price_drop_value):
    result_list = []
    i = 0
    while i < len(iv_quotes) or (i is None):
        i = find_iv_spike(iv_quotes, iv_entropy_value, i, i + iv_entropy_period)

        if i is None:
            break

        if price_quotes[i - 5].value > price_quotes[i].value * (1 + price_drop_value):
            result_list.append(iv_quotes[i].date)
            i = find_iv_stabilization(iv_quotes, iv_calm_value, i, i + iv_calm_period)

        else:
            i += 1

    return result_list


def find_iv_spike(quotes_list, iv_entropy_value, start_index, end_index):
    try:
        while start_index < len(quotes_list):
            max_quote = trd.Quote.find_first_max_quote(quotes_list[start_index:end_index])
            max_quote_index = quotes_list.index(max_quote)

            if max_quote_index > start_index:
                min_quote = trd.Quote.find_first_min_quote(
                    quotes_list[start_index:max_quote_index])  # min всегда должен быть раньше чем max

                diff = (max_quote.value - min_quote.value) / min_quote.value

                if diff >= iv_entropy_value:
                    return max_quote_index

            start_index += 1
            end_index += 1

    except BaseException as exception:
        print(exception, start_index)


def find_iv_stabilization(quotes_list, iv_calm_value, start_index, end_index):
    while start_index < len(quotes_list):
        max_quote = trd.Quote.find_first_max_quote(quotes_list[start_index:end_index])
        min_quote = trd.Quote.find_first_min_quote(quotes_list[start_index:end_index])
        diff = (max_quote.value - min_quote.value) / min_quote.value

        if diff <= iv_calm_value:
            return end_index

        start_index += 1
        end_index += 1


main()
