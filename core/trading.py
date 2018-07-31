import datetime
import math


def get_calendars_dayoffs():
    return [
        datetime.date(2015, 1, 1),
        datetime.date(2015, 1, 19),
        datetime.date(2015, 2, 16),
        datetime.date(2015, 4, 3),
        datetime.date(2015, 5, 25),
        datetime.date(2015, 7, 3),
        datetime.date(2015, 9, 7),
        datetime.date(2015, 11, 26),
        datetime.date(2015, 12, 25),
        datetime.date(2016, 1, 1),
        datetime.date(2016, 1, 18),
        datetime.date(2016, 2, 15),
        datetime.date(2016, 3, 25),
        datetime.date(2016, 5, 30),
        datetime.date(2016, 7, 4),
        datetime.date(2016, 9, 5),
        datetime.date(2016, 11, 24),
        datetime.date(2016, 12, 26),
        datetime.date(2017, 1, 2),
        datetime.date(2017, 1, 16),
        datetime.date(2017, 2, 20),
        datetime.date(2017, 4, 14),
        datetime.date(2017, 5, 29),
        datetime.date(2017, 7, 4),
        datetime.date(2017, 9, 4),
        datetime.date(2017, 11, 23),
        datetime.date(2017, 12, 25),
        datetime.date(2018, 1, 1),
        datetime.date(2018, 1, 15),
        datetime.date(2018, 2, 19),
        datetime.date(2018, 3, 30),
        datetime.date(2018, 5, 28),
        datetime.date(2018, 7, 4),
        datetime.date(2018, 9, 3),
        datetime.date(2018, 11, 22),
        datetime.date(2018, 12, 25),
    ]


class Deal:
    BUY_DEAL_TYPE = "BUY"
    SELL_DEAL_TYPE = "SELL"

    def __init__(self, tradedate, exitdate, enterprice, exitprice, quantity, description):
        self.__tradedate = tradedate
        self.__exitdate = exitdate
        self.__enterprice = enterprice
        self.__exitprice = exitprice
        self.__quantity = quantity
        self.__description = description

    @property
    def tradedate(self):
        return self.__tradedate

    @property
    def exitdate(self):
        return self.__exitdate

    @property
    def enterprice(self):
        return self.__enterprice

    @property
    def exitprice(self):
        return self.__exitprice

    @property
    def quantity(self):
        return self.__quantity

    @property
    def description(self):
        return self.__description

    def __repr__(self):
        return "Deal trade date:{} | " \
               "exit date:{} |" \
               "enter price:{} | " \
               "exit price:{} | " \
               "quantity:{} | " \
               "description:{} | ".format(self.tradedate, self.exitdate, self.enterprice,
                                          self.exitprice, self.quantity, self.description)

    def get_deal_pnl(self):
        return (self.exitprice - self.enterprice) * self.quantity


class OptionDeal(Deal):
    OPTION_CALL_TYPE = "CALL"
    OPTION_PUT_TYPE = "PUT"

    def __init__(self, tradedate, exitdate, enterprice, exitprice, quantity, description, spotref_enter, spotref_exit):
        Deal.__init__(self, tradedate, exitdate, enterprice, exitprice, quantity, description)
        self.__spotref_enter = spotref_enter
        self.__spotref_exit = spotref_exit

    @property
    def spotref_enter(self):
        return self.__spotref_enter

    @property
    def spotref_exit(self):
        return self.__spotref_exit

    def __repr__(self):
        return "OptionDeal trade date:{} |" \
               "exit date:{} |" \
               "enter price:{:7} |" \
               "exit price:{:7} |" \
               "q:{:3} |" \
               "description:{:25} |" \
               "spotref_enter:{:7} |" \
               "spotref_exit:{:7}  ".format(self.tradedate, self.exitdate, self.enterprice,
                                            self.exitprice, self.quantity, self.description,
                                            self.spotref_enter, self.spotref_exit)

    @classmethod
    def create_option_deal(cls, o_d_r_enter, o_d_r_exit, quantity_abs, deal_type):
        if o_d_r_enter.generate_id() != o_d_r_exit.generate_id():
            raise AttributeError("enter and exit o_d_r have different ID - wrong logic")

        description = str(deal_type + o_d_r_enter.generate_id())

        if deal_type == Deal.BUY_DEAL_TYPE:
            enter_price = o_d_r_enter.ask
            exit_price = o_d_r_exit.bid
        elif deal_type == Deal.SELL_DEAL_TYPE:
            enter_price = o_d_r_enter.bid
            exit_price = o_d_r_exit.ask
            quantity_abs = quantity_abs * -1
        else:
            print("wrong type of deal, have a look at class trading.Deal")
            return None

        return OptionDeal(o_d_r_enter.tradedate, o_d_r_exit.tradedate, enter_price, exit_price,
                          quantity_abs, description, o_d_r_enter.spotref, o_d_r_exit.spotref)


class Quote:

    @staticmethod
    def find_first_max_quote(quotes_list):
        values_dict = {}
        for quote in quotes_list:
            key = values_dict.get(quote.value)

            if key is None:
                values_dict[quote.value] = quote

        return values_dict[max(values_dict.keys())]

    @staticmethod
    def find_first_min_quote(quotes_list):
        values_dict = {}
        for quote in quotes_list:
            key = values_dict.get(quote.value)

            if key is None:
                values_dict[quote.value] = quote

        return values_dict[min(values_dict.keys())]

    def __init__(self, date, value):
        self.__date = date
        self.__value = float(value)

    @property
    def date(self):
        return self.__date

    @property
    def value(self):
        return self.__value

    def __repr__(self):
        return "Quote date: {} |" \
               "value: {:7}".format(self.date, self.value)


class BidAskQuote:

    def __init__(self, date, bid, ask):
        self.__date = date
        self.__bid = float(bid)
        self.__ask = float(ask)

    @property
    def date(self):
        return self.__date

    @property
    def bid(self):
        return self.__bid

    @property
    def ask(self):
        return self.__ask

    def __repr__(self):
        return "Quote date: {} |" \
               "bid/ask: {:4}/{:4}".format(self.date, self.bid, self.ask)


# useful methods
def get_nearest_friday(date):
    day_diff = 5 - date.isoweekday()

    if day_diff >= 0:
        return date + datetime.timedelta(day_diff)  # nearest this week friday
    else:
        return date + datetime.timedelta(math.fabs(7) - math.fabs(day_diff))  # next week friday


def subtract_workdays_from_date(date, n):
    return work_days_shifting(date, n, -1)


def add_workdays_to_date(date, n):
    return work_days_shifting(date, n, 1)


def work_days_shifting(date, n, sign):
    while n != 0:
        date = date + sign * datetime.timedelta(1)  # one day shifting
        if not is_dayoff(date):
            n -= 1

    return date


def is_dayoff(date):
    holidays = get_calendars_dayoffs()

    if date.isoweekday() == 6 \
            or date.isoweekday() == 7 \
            or date in holidays:

        return True
    else:
        return False


def rounding_to_strike_step(price, round_to):
    main_part = round(price / round_to, 0) * round_to
    fraction_part = price - main_part

    if fraction_part < float(round_to / 2):
        return main_part
    else:
        return main_part + round_to


def define_strike_step(current_price):
    if current_price >= 150:
        return 2.5
    elif current_price >= 100:
        return 1
    else:
        return 0.5
