import csv
import datetime
from core import trading as trd


class HistoricalDataReader:

    def __init__(self, file_name, file_date_format="%m/%d/%Y"):
        self.__file_name = file_name
        self.__file_date_format = file_date_format
        self.__tickers = []
        self.__historical_data = {}

    def convert_data_from_file(self, delimiter=','):
        with open(self.__file_name) as CSV_file:
            data_reader = csv.reader(CSV_file, delimiter=delimiter)

            headers_read = False

            for primal_data_row in data_reader:

                if headers_read is False:
                    for element in list(filter(None, primal_data_row)):
                        ticker = element[:element.find(' ')]
                        self.__tickers.append(ticker)

                    for ticker in self.__tickers:
                        self.__historical_data[ticker] = []

                    headers_read = True
                    continue

                date = FinancialDataHelper.convert_str_to_date(primal_data_row[0], self.__file_date_format)
                start_index = 1
                end_index = len(primal_data_row) - 2

                for i in range(start_index, end_index):
                    quote = trd.Quote(date, float(primal_data_row[i]))
                    self.__historical_data[self.__tickers[i - 1]].append(quote)

    def get_tickers_list(self):
        return self.__tickers

    def get_historical_data_dict(self):
        return self.__historical_data


class OptionsDataReader:

    def __init__(self, file_name, date_cl, spotref_cl, opttype_cl,
                 strike_cl, bid_cl, ask_cl, expiration_cl, contains_headers=False):
        self.file_name = file_name
        self.date_cl = date_cl - 1
        self.spotref_cl = spotref_cl - 1
        self.opttype_cl = opttype_cl - 1
        self.stike_cl = strike_cl - 1
        self.bid_cl = bid_cl - 1
        self.ask_cl = ask_cl - 1
        self.expiration_cl = expiration_cl - 1
        self.__options_data = {}
        self.__spot_ref_data = {}
        self.contains_headers = contains_headers

    def convert_data_from_file(self, delimiter=','):
        with open(self.file_name) as CSV_file:
            data_reader = csv.reader(CSV_file, delimiter=delimiter)

            if self.contains_headers is True:
                check_headers = False
            else:
                check_headers = True

            for primal_data_row in data_reader:

                if check_headers is False:
                    check_headers = True
                    continue

                date = FinancialDataHelper.convert_str_to_date(primal_data_row[self.date_cl])

                options_data_dict = self.__options_data.get(date)

                option_data_row = OptionsDataRow(
                    primal_data_row[self.date_cl],
                    primal_data_row[self.spotref_cl],
                    primal_data_row[self.opttype_cl],
                    primal_data_row[self.stike_cl],
                    primal_data_row[self.bid_cl],
                    primal_data_row[self.ask_cl],
                    primal_data_row[self.expiration_cl])

                if options_data_dict is None:
                    self.__options_data[date] = {option_data_row.generate_id(): option_data_row}
                else:
                    options_data_dict[option_data_row.generate_id()] = option_data_row

                if not (date in self.__spot_ref_data.keys()):
                    self.__spot_ref_data[date] = option_data_row.spotref

    def get_options_dict_by_date(self, tradedate):
        return self.__options_data.get(tradedate)

    def get_option_by_args(self, tradedate, opttype, expiration, strike):
        data_dict = self.get_options_data_dict()

        if data_dict is not None:
            return data_dict[tradedate][OptionsDataRow.make_option_id(opttype, expiration, strike)]

    def get_option_by_option_id(self, tradedate, option_id):
        data_dict = self.get_options_data_dict()

        if data_dict is not None:
            return data_dict[tradedate].get(option_id)

    def get_price_data_by_date(self, date):
        temp_dict = self.get_price_data_dict()

        if temp_dict is not None:
            return temp_dict[date]

    def get_options_data_dict(self):
        if self.__options_data is None:
            print("you have to read file first")
            return None
        else:
            return self.__options_data

    def get_price_data_dict(self):
        if self.__spot_ref_data is None:
            print("you have to read file first")
            return None
        else:
            return self.__spot_ref_data

    def get_option_historical_prices(self, option_id):
        temp_dict = self.get_options_data_dict()

        str_expiration_date = option_id[len(option_id) - 10:]
        expiration_date = FinancialDataHelper.convert_str_to_date(str_expiration_date,
                                                                  convert_format=FinancialDataHelper.get_str_date_internal_default_format())
        option_prices = {}

        for key in temp_dict:
            if key > expiration_date:
                break

            option = self.get_option_by_option_id(key, option_id)

            if option is not None:
                option_prices[key] = trd.BidAskQuote(key, option.bid, option.ask)

        return option_prices


class OptionsDataRow:

    @staticmethod
    def make_option_id(opttype, expiration, strike):
        return str(float(strike)) + opttype + expiration.strftime(
            FinancialDataHelper.get_str_date_internal_default_format())

    def __init__(self, tradedate, spotref, opttype, strike, bid, ask, expiration):
        self.__tradedate = FinancialDataHelper.convert_str_to_date(tradedate)
        self.__spotref = float(spotref)
        self.__opttype = trd.OptionDeal.OPTION_CALL_TYPE \
            if ("C" or "c") in opttype \
            else trd.OptionDeal.OPTION_PUT_TYPE
        self.__strike = float(strike)
        self.__bid = float(bid)
        self.__ask = float(ask)
        self.__expiration = FinancialDataHelper.convert_str_to_date(expiration)

    @property
    def tradedate(self):
        return self.__tradedate

    @property
    def spotref(self):
        return self.__spotref

    @property
    def opttype(self):
        return self.__opttype

    @property
    def strike(self):
        return self.__strike

    @property
    def bid(self):
        return self.__bid

    @property
    def ask(self):
        return self.__ask

    @property
    def expiration(self):
        return self.__expiration

    def generate_id(self):
        return OptionsDataRow.make_option_id(self.opttype, self.expiration, self.strike)

    def __repr__(self):
        return "OptionsDataRow trade date:{} | " \
               "stock price:{} | " \
               "type:{} | " \
               "expiration:{} | " \
               "strike:{} | " \
               "bid:{} | " \
               "ask:{}".format(self.tradedate, self.spotref,
                               self.opttype, self.expiration,
                               self.strike, self.bid, self.ask)


class FinancialDataHelper:

    @staticmethod
    def get_str_date_external_default_format():
        return "%m/%d/%Y"

    @staticmethod
    def get_str_date_internal_default_format():
        return "%Y-%m-%d"

    @staticmethod
    def convert_str_to_date(str_date, convert_format=None):
        if convert_format is None:
            convert_format = FinancialDataHelper.get_str_date_external_default_format()
        return datetime.datetime.strptime(str_date, convert_format).date()

    @staticmethod
    def convert_date_to_str(date, convert_format=None):
        if convert_format is None:
            convert_format = FinancialDataHelper.get_str_date_internal_default_format()
        return datetime.datetime.strftime(date, convert_format)

    @staticmethod
    def read_dates_from_file(file_name, delimiter=','):
        report_dates = []
        with open(file_name) as CSV_file:
            primal_data = csv.reader(CSV_file, delimiter=delimiter)

            for row in primal_data:
                report_dates.append(FinancialDataHelper.convert_str_to_date(row[0], "%d.%m.%Y"))

            return report_dates
