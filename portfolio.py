__author__ = 'jams'

# import xml.etree.ElementTree as ET
from datetime import datetime
from lxml import etree as ET
import ystockquote as ys

class PortfolioAsset:

    def __init__(self,element=None):
        if element is None:
            asset_id = 0
            name = ''
            market = ''
            symbol = ''
            currency = ''
            units = 0
            purchase_price = {'date' : None,'value' : 0.0}
            previous_close = {'date' : None,'value' : 0.0}
            maximum_close = {'date' : None,'value' : 0.0}
            minimum_close = {'date' : None,'value' : 0.0}
            stop_price = 0.0
            add_units_price = 0.0
        else:
            # asset_id
            asset_id = int(element.attrib['id'])
            # name
            name = get_text_from_xml(element,'name')
            # market
            market = get_text_from_xml(element,'market')
            # symbol
            symbol = get_text_from_xml(element,'symbol')
            # currency
            currency = get_text_from_xml(element,'currency')
            # units
            units = int(get_text_from_xml(element,'units'))
            # purchase_price
            purchase_price = get_dict_from_xml(element,'purchase_price')
            # previous_close
            previous_close = get_dict_from_xml(element,'previous_close')
            # maximum_close
            maximum_close = get_dict_from_xml(element,'maximum_close')
            # minimum_close
            minimum_close = get_dict_from_xml(element,'minimum_close')
            # stop_price
            stop_price = float(get_text_from_xml(element,'stop_price'))
            # add_units_price
            add_units_price = float(get_text_from_xml(element,
                                                      'add_units_price'))
        self.asset_id = asset_id
        self.name = name
        self.market = market
        self.symbol = symbol
        self.currency = currency
        self.units = units
        self.purchase_price = purchase_price
        self.previous_close = previous_close
        self.maximum_close = maximum_close
        self.minimum_close = minimum_close
        self.stop_price = stop_price
        self.add_unit_price = add_units_price

    def value(self):
        """  Returns current market value """
        return self.previous_close['value']*self.units

    def add_units(self,purchase_price_dict,units):
        """ Add units to the asset """
        output_message = []
        if purchase_price_dict.keys() != self.purchase_price.keys():
            output_message.append('Wrong keys in purchase_price_dict while'
                                  ' adding units to {}'.format(self.name))
        elif units <= 0:
            output_message.append('Units lower or equal 0 while adding units'
                                  ' to {}'.format(self.name))
        else:
            self.units += units
            self.purchase_price['value'] = purchase_price_dict['value']
            self.purchase_price['date'] = datetime.strptime(
                purchase_price_dict['date'],'%Y-%m-%d')
            output_message.append('Added {} units to {} at {} {} on {}'.
                                  format(units, self.name,
                                         self.purchase_price['value'],
                                         self.currency,
                                         self.purchase_price['date']))
        return output_message

    def remove_units(self,sell_price_dict,units):
        """ Remove units from the asset """
        output_message = []
        if sell_price_dict.keys() != self.purchase_price.keys():
            output_message.append('Wrong keys in sell_price_dict while'
                                  ' removing units from {}'.format(self.name))
        elif units >= self.units:
            output_message.append('Units greater or equal to owned units in {}'
                                  .format(self.name))
        else:
            self.units -= units
            self.purchase_price['value'] = sell_price_dict['value']
            self.purchase_price['date'] = datetime.strptime(
                sell_price_dict['date'],'%Y-%m-%d')
            output_message.append('Removed {} units from {} at {} {} on {}'.
                                  format(units, self.name,
                                         self.purchase_price['value'],
                                         self.currency,
                                         self.purchase_price['date']))
        return output_message


class MyPortfolio:

    file_name = 'PruebaPortfolio.xml'

    """ Class variables """
    initial_capital = {'currency' : '', 'value' : 0.0}
    total_capital = {'currency' : '', 'value' : 0.0}
    invested_capital = {'currency' : '', 'value' : 0.0}
    not_invested_capital = {'currency' : '', 'value' : 0.0}
    performance = {'units' : '%', 'value' : 0.0}
    portfolio = []

    def __init__(self, file_name):
        self.file_name = file_name
        self.init_portfolio(file_name)

    def init_portfolio(self, file_name):
        tree = ET.parse(file_name)
        # PENDIENTE!!: Dar un error en caso que devuelva un diccionario vacío
        """ initial_capital """
        self.initial_capital = get_xml_capital_value(tree,'initial_capital')
        """ total_capital """
        self.total_capital = get_xml_capital_value(tree,'total_capital')
        """ invested_capital """
        self.invested_capital = get_xml_capital_value(tree,'invested_capital')
        """ not_invested_capital """
        self.not_invested_capital = get_xml_capital_value(tree,
                'not_invested_capital')
        """ performance """
        self.performance = get_xml_performance_value(tree,'performance')
        """ portfolio list """
        element = tree.find('portfolio')
        if element is not None:
            for asset in element:
                self.portfolio.append(PortfolioAsset(asset))

    def increase_capital(self, new_capital, update_xml=False):
        """ Increase portfolio capital for investment from an external account.

        Args:
        new_capital: amount of new capital to the portfolio account
        update_xml: True to update xml file after the operation

        Returns:
        List of messages (errors or comments)
        """
        output_message = []
        if new_capital <= 0:
            output_message.append('Capital lower or equal 0')
        else:
            self.initial_capital['value'] += new_capital
            ouput_message.append('Capital increased. New initial capital = {}'
                                 ' {}'.format(self.initial_capital['value'],
                                              self.initial_capital['currency']))
            if update_xml:
                output_message.append(self.update_xml_file())
        return output_mesage

    def withdraw_capital(self, remove_capital, update_xml=False):
        """ Reduce portfolio capital for investment.

        Args:
        remove_capital: amount of capital to be withdrawn from the portfolio
            account
        update_xml: True to update xml file after the operation

        Returns:
        List of messages (errors or comments)
        """
        output_message = []
        if remove_capital > self.not_invested_capital['value']:
            ouput_message.append('Capital higher than capital in account')
        else:
            self.initial_capital['value'] -= remove_capital
            ouput_message.append('Capital reduced. New initial capital = {} {}'
                                 .format(self.initial_capital['value'],
                                         self.initial_capital['currency']))
            if update_xml:
                output_message.append(self.update_xml_file())
        return output_mesage

    def search_asset(self, asset_id_dict):
        """ Search an asset in the portfolio

        Args:
        asset_id_dict: Dictionary containing at least one of the following
            keys: 'asset_id', 'symbol', 'name', used to find the asset.

        Returns:
        If the asset is found, it returns the index. In other case, it returns
        None.
        """
        asset_found = False
        for index, asset in enumerate(self.portfolio):
            asset_found = True
            for k in asset_id_dict:
                if k not in asset.__dict__:
                    # key not found in the asset
                    asset_found = False
                elif asset_id_dict[k] != asset.__dict__[k]:
                    # value doesn't match
                    asset_found = False

            if asset_found:
                # asset found, stop loop
                break

        if asset_found:
            return index
        else:
            return None

    def add_units(self, asset_id_dict, purchase_price_dict, units,
                  update_xml=False):
        """ Increase number of units of an asset already in the portfolio.

        Args:
        asset_id_dict: Dictionary containing at least one of the following
            keys: 'asset_id', 'symbol', 'name', used to find the asset.
        purchase_price_dict: Dictionary containing the 'value' and 'date' of
            the purchase of the asset.
        units: number of units bought at purchase_price_dict
        update_xml: True to update xml file after the operation

        Returns:
        List of messages (errors or comments)
        """
        # Buffer with messages to return
        output_message = []
        if asset_id_dict is None:
            output_message.append('Empty search dictionary')
        elif purchase_price_dict is None:
            output_message.append('Not purchase price given')
        elif units <= 0:
            output_message.append('Number of units lower or equal 0')
        elif ('asset_id' not in asset_id_dict) and ('symbol' not in
            asset_id_dict) and ('name' not in asset_id_dict):
            output_message.append('Wrong keys in asset_id_dict')
        else:
            index = self.search_asset(asset_id_dict)
            if index is not None:
                if ('value' not in purchase_price_dict) or ('date' not in
                    purchase_price_dict):
                    output_message.append('Wrong keys in purchase_price_dict')
                else:
                    output_message += (self.portfolio[index].
                                       add_units(purchase_price_dict, units))
                    if update_xml:
                        output_message.append(self.update_xml_file())
            else:
                output_message.append('Asset not found')

        return output_message

    def remove_units(self, asset_id_dict, sell_price_dict, units,
                     update_xml=False):
        """ Reduce number of units of an asset already in the portfolio.

        Args:
        asset_id_dict: Dictionary containing at least one of the following
            keys: 'asset_id', 'symbol', 'name', used to find the asset.
        sell_price_dict: Dictionary containing the 'value' and 'date' of
            the selling of the asset.
        units: number of units sold at sell_price_dict
        update_xml: True to update xml file after the operation

        Returns:
        List of messages (errors or comments)
        """
        # Buffer with messages to return
        output_message = []
        if asset_id_dict is None:
            output_message.append('Empty search dictionary')
        elif sell_price_dict is None:
            output_message.append('Not sell price given')
        elif units <= 0:
            output_message.append('Number of units lower or equal 0')
        elif ('asset_id' not in asset_id_dict) and ('symbol' not in
            asset_id_dict) and ('name' not in asset_id_dict):
            output_message.append('Wrong keys in asset_id_dict')
        else:
            index = self.search_asset(asset_id_dict)
            if index is not None:
                if ('value' not in sell_price_dict) or ('date' not in
                    sell_price_dict):
                    output_message.append('Wrong keys in sell_price_dict')
                else:
                    output_message += (self.portfolio[index].
                                       remove_units(sell_price_dict, units))
                    if update_xml:
                        output_message.append(self.update_xml_file())
            else:
                output_message.append('Asset not found')

        return output_message

    def update_xml_file(self):
        """ Create a new xml file with the updated data in the class.
        Every time this method is called, a new file is created with a date
        and time stamp.

        Returns:
        String with the name of the new file
        """
        update_date = datetime.now()
        root = ET.Element('MyPortfolio')
        """ update_date """
        ET.SubElement(root, 'update_date').text = str(update_date).split('.')[0]
        """ initial_capital """
        ET.SubElement(root, 'initial_capital',
                      currency=self.initial_capital['currency']).text = str(
            self.initial_capital['value']
        )
        """ total_capital """
        ET.SubElement(root, 'total_capital',
                      currency=self.total_capital['currency']).text = str(
            self.total_capital['value']
        )
        """ invested_capital """
        ET.SubElement(root, 'invested_capital',
                      currency=self.invested_capital['currency']).text = str(
            self.invested_capital['value']
        )
        """ not_invested_capital """
        ET.SubElement(root, 'not_invested_capital',
                      currency=self.not_invested_capital['currency']).text = (
            str(self.not_invested_capital['value'])
        )
        """ performance """
        ET.SubElement(root, 'performance',
                      units=self.performance['units']).text = str(
            self.performance['value']
        )
        """ portfolio """
        portfolio = ET.SubElement(root, 'portfolio')
        for asset in self.portfolio:
            asset_element = ET.SubElement(portfolio, 'asset', id=str(
                asset.asset_id))
            ET.SubElement(asset_element, 'name').text = asset.name
            ET.SubElement(asset_element, 'market').text = asset.market
            ET.SubElement(asset_element, 'symbol').text = asset.symbol
            ET.SubElement(asset_element, 'currency').text = asset.currency
            ET.SubElement(asset_element, 'units').text = str(asset.units)
            ET.SubElement(asset_element, 'purchase_price', date=
                asset.purchase_price['date'].strftime('%Y-%m-%d')).text = (
                str(asset.purchase_price['value'])
            )
            ET.SubElement(asset_element, 'previous_close', date=
                asset.previous_close['date'].strftime('%Y-%m-%d')).text = (
                str(asset.previous_close['value'])
            )
            ET.SubElement(asset_element, 'maximum_close', date=
                asset.maximum_close['date'].strftime('%Y-%m-%d')).text = (
                str(asset.maximum_close['value'])
            )
            ET.SubElement(asset_element, 'minimum_close', date=
                asset.minimum_close['date'].strftime('%Y-%m-%d')).text = (
                str(asset.minimum_close['value'])
            )
            ET.SubElement(asset_element, 'stop_price').text = str(
                asset.stop_price)
            ET.SubElement(asset_element, 'add_units_price').text = str(
                asset.add_units_price)

        tree = ET.ElementTree(root)

        # e.g. 'JamsPortfolio-2015-04-12--20-29-30.xml'
        if len(self.file_name.split('.')[0]) > 20:
            file_name = (self.file_name.split('.')[0][0:-20] +
                         update_date.strftime('%Y-%m-%d--%H-%M-%S') + '.xml')
        else:
            file_name = (self.file_name.split('.')[0] + '-' +
                         update_date.strftime('%Y-%m-%d--%H-%M-%S') + '.xml')

        # point to new file
        self.file_name = file_name

        tree.write(file_name, pretty_print=True)

        # print xml tree on console
        ET.dump(root)

        return 'XML file created: ' + file_name

    def update_close_prices(self, update_xml=False, provider='Yahoo'):
        """ Update
        :return:
        """

        output_message = []

        for asset in self.portfolio:
            if provider == 'Yahoo':
                try:
                    # get last trade date of the asset
                    last_trade_date_str = \
                        ys.get_last_trade_date(asset.symbol).replace('"','')
                    if last_trade_date_str == 'N/A':
                        output_message.append('{} symbol ({}) not found'.
                                              format(asset.name,asset.symbol))
                        continue
                    else:
                        last_trade_date = \
                            datetime.strptime(last_trade_date_str,'%m/%d/%Y')
                except:
                    output_message.append('Data of {} not available in '
                                              'provider'.format(asset.name))
                    continue


                if last_trade_date > asset.previous_close['date']:

                    try:
                        # update maximum_close and minimum_close
                        hist_dict = ys.get_historical_prices(
                            asset.symbol,
                            asset.previous_close['date'].strftime('%Y-%m-%d'),
                            last_trade_date.strftime('%Y-%m-%d'))
                        # parse all dictionary
                        for td, tv in hist_dict.items():
                            item_date = datetime.strptime(td, '%Y-%m-%d')
                            item_close = float(tv['Close'])

                            # previous close
                            if item_date > asset.previous_close['date']:
                                asset.previous_close['date'] = item_date
                                asset.previous_close['value'] = item_close
                                output_message.append('Previous close has been '
                                                    'updated - Date: {} - '
                                                    'Close: {}'.
                                                    format(item_date,
                                                           item_close))
                            # maximum close
                            if item_close > asset.maximum_close['value']:
                                # new maximum close found
                                asset.maximum_close['date'] = item_date
                                asset.maximum_close['value'] = item_close
                                output_message.append('Maximum close has been '
                                                    'updated - Date: {} - '
                                                    'Close: {}'.
                                                    format(item_date,
                                                           item_close))
                            if item_close < asset.minimum_close['value']:
                                # new maximum close found
                                asset.minimum_close['date'] = item_date
                                asset.minimum_close['value'] = item_close
                                output_message.append('Minimum close has been '
                                                    'updated - Date: {} - '
                                                    'Close: {}'.
                                                    format(item_date,
                                                           item_close))

                    except:
                        output_message.append('Data of {} not available in '
                                              'provider'.format(asset.name))

        # update xml
        if update_xml:
            output_message.append(self.update_xml_file())

        return output_message


def get_xml_capital_value(tree,field_text):
    """Search a capital entry (currency+value) in a xml tree and return a
    dictionary with the following keys: {'currency':(string),'value':(float)}

    Args:
        tree: ElementTree object
        field_text: string which the tag to find

    Returns:
        dictionary {'currency':(string),'value':(float)}
        or empty dictionary in case entry not found or not capital type
    """
    output_dict = {}
    element = tree.find(field_text)
    if element is not None and 'currency' in element.attrib.keys():
        output_dict['value'] = float(element.text)
        output_dict.update(element.attrib)
    return output_dict


def get_xml_performance_value(tree,field_text):
    """Search a performance entry (units+value) in a xml tree and return a
    dictionary with the following keys: {'units':(string),'value':(float)}

    Args:
        tree: ElementTree object
        field_text: string which the tag to find

    Returns:
        dictionary {'units':(string),'value':(float)}
        or empty dictionary in case entry not found or not capital type
    """
    output_dict = {}
    element = tree.find(field_text)
    if element is not None and 'units' in element.attrib.keys():
        output_dict['value'] = float(element.text)
        output_dict.update(element.attrib)
    return output_dict

def set_xml_capital_value(tree,field_text,capital_dict):
    """Search a capital entry (currency+value) in a xml tree and modifies
    the ET element according to capital_dict:
    {'currency':(string),'value':(float)}

    Args:
        tree: ElementTree object
        field_text: string which the tag to find
        capital_dict: modified dictionary {'currency':(string),'value':(float)}

    Returns:
        None
    """
    element = tree.find(field_text)
    if element is not None and 'currency' in element.attrib.keys():
        element.attrib['currency'] = capital_dict['currency']
        element.text = capital_dict['value']

def get_text_from_xml(element,field_text):
    """ Search a field in a xml element and returns its text

    :param element: xml element
    :param field_text: string with the field name to search
    :return: string with the field text value. None is not found.
    """
    child = element.find(field_text)
    if child is not None:
        return child.text

def get_dict_from_xml(element,field_text):
    """ Search a field with date and value in a xml element and returns a
    dictionary with date and value keys

    :param element: xml element
    :param field_text: string with the field name to search
    :return: dictionary {'date': datetime, 'value': float}
    """
    child = element.find(field_text)
    if child is not None and 'date' in child.attrib.keys():
        output_dict = {}
        output_dict['date'] = datetime.strptime(child.attrib['date'],'%Y-%m-%d')
        output_dict['value'] = float(child.text)
        return output_dict