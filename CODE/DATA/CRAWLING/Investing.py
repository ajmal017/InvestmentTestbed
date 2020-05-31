# _*_ coding: utf-8 _*_

import urllib
import urllib.request
import requests
from urllib.error import HTTPError

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium import common
import datetime
import time
import sys
import os
from itertools import count
import arrow
import re
import timeit
import platform
import pandas as pd
from datetime import datetime
from datetime import timedelta
from datetime import date


def getRealValue(s):
    try:
        if len(s) == 0:
            value = 'NULL'
            unit = 'NULL'
        else:
            s = s.replace(',', '')
            if s[-1].upper() == 'K':
                value = float(s[:-1])
                unit = 1000
            elif s[-1].upper() == 'M':
                value = float(s[:-1])
                unit = 1000000
            elif s[-1].upper() == 'B':
                value = float(s[:-1])
                unit = 1000000000
            elif s[-1] == '%':
                value = float(s[:-1])
                unit = 0.01
            elif s[-1] == '-':
                value = 0.0
                unit = 1
            else:
                value = float(s)
                unit = 1

        return value, unit

    except (ValueError, TypeError) as e:
        print('에러정보 : ', e, file=sys.stderr)

        value = 0.0
        unit = 1

        return value, unit

def removeAd(wd):
    all_iframes = wd.find_elements_by_tag_name("iframe")
    if len(all_iframes) > 0:
        #print("Ad Found\n")
        wd.execute_script("""
                    var elems = document.getElementsByTagName("iframe"); 
                    for(var i = 0, max = elems.length; i < max; i++)
                         {
                             elems[i].hidden=true;
                         }
                                      """)
        #print('Total Ads: ' + str(len(all_iframes)))
    else:
        pass
        #print('No frames found')


class Good():
    def __init__(self):
        self.value = "+"
        self.name = "good"

    def __repr__(self):
        return "<Good(value='%s')>" % (self.value)


class Bad():
    def __init__(self):
        self.value = "-"
        self.name = "bad"

    def __repr__(self):
        return "<Bad(value='%s')>" % (self.value)


class Unknow():
    def __init__(self):
        self.value = "?"
        self.name = "unknow"

    def __repr__(self):
        return "<Unknow(value='%s')>" % (self.value)


class InvestingEconomicCalendar():
    def __init__(self, uri='https://www.investing.com/economic-calendar/', country_list=None):
        self.uri = uri
        self.req = urllib.request.Request(uri)
        self.req.add_header('User-Agent',
                            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36')
        self.country_list = country_list
        self.result = []

    def getEvents(self):
        try:
            response = urllib.request.urlopen(self.req)
            html = response.read()
            soup = BeautifulSoup(html, "html.parser")

            # Find event item fields
            table = soup.find('table', {"id": "economicCalendarData"})
            tbody = table.find('tbody')
            rows = tbody.findAll('tr', {"class": "js-event-item"})

            for row in rows:
                events = {}
                _datetime = row.attrs['data-event-datetime']
                events['timestamp'] = arrow.get(_datetime, "YYYY/MM/DD HH:mm:ss").timestamp
                events['date'] = _datetime[0:10]

                cols = row.find('td', {"class": "flagCur"})
                flag = cols.find('span')
                events['country'] = flag.get('title')

                # 예외 국가 필터링
                if self.country_list is not None and events['country'] not in self.country_list:
                    continue

                impact = row.find('td', {"class": "sentiment"})
                bull = impact.findAll('i', {"class": "grayFullBullishIcon"})
                events['impact'] = len(bull)

                event = row.find('td', {"class": "event"})
                a = event.find('a')
                events['url'] = "{}{}".format(self.uri, a['href'][a['href'].find('/', 2) + 1:])
                events['name'] = a.text.strip()

                # Determite type of event
                events['type'] = None
                if event.find('span', {"class": "smallGrayReport"}):
                    events['type'] = "report"
                elif event.find('span', {"class": "audioIconNew"}):
                    events['type'] = "speech"
                elif event.find('span', {"class": "smallGrayP"}):
                    events['type'] = "release"
                elif event.find('span', {"class": "sandClock"}):
                    events['type'] = "retrieving data"

                bold = row.find('td', {"class": "bold"})
                events['bold'] = bold.text.strip() if bold.text != '' else ''

                fore = row.find('td', {"class": "fore"})
                events['fore'] = fore.text.strip() if fore.text != '' else ''

                prev = row.find('td', {"class": "prev"})
                events['prev'] = prev.text.strip() if prev.text != '' else ''

                if "blackFont" in bold['class']:
                    events['signal'] = Unknow()
                elif "redFont" in bold['class']:
                    events['signal'] = Bad()
                elif "greenFont" in bold['class']:
                    events['signal'] = Good()
                else:
                    events['signal'] = Unknow()

                print(events)
                self.result.append(events)

        except HTTPError as error:
            print("Oops... Get error HTTP {}".format(error.code))

        return self.result


calendar_map = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6, 'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
              , 'Q1': 1, 'Q2': 2, 'Q3': 3, 'Q4': 4}
group_country_dict = {'United States all stocks': 'US', 'NASDAQ Composite': 'US', 'KOSPI 200': 'KR', 'KOSDAQ 150': 'KR', 'S&P 500': 'US', 'Nasdaq 100': 'US'}

def CrawlingStart(obj, t_gap, loop_num):
    obj.Start(t_gap=t_gap, loop_num=loop_num)

class InvestingStockInfo():
    def __init__(self, db, country='KR', group='KOSPI 200'):
        self.db = db
        self.country = country
        self.group = group

        self.root_dir = 'https://www.investing.com'
        self.equity_dir = '%s/equities' % (self.root_dir)
        self.country_equity_dir = {'KR': '%s/south-korea' % (self.equity_dir), 'US': '%s/united-states' % (self.equity_dir)}

        self.profile_sub = '-company-profile'
        self.financial_sub = '-financial-summary'
        self.earnings_sub = '-earnings'
        self.dividends_sub = '-dividends'
        self.price_sub = '-historical-data'

    def getWebDriver(self,do_background):
        options = webdriver.ChromeOptions()

        # 크롬을 BackGround에서 실행할 경우
        if do_background == True:
            options.add_argument('headless')
            #options.add_argument('window-size=1920x1080')
            # 혹은 options.add_argument("--disable-gpu")
            #options.add_argument("disable-gpu")
        options.add_argument("--disable-popup-blocking")

        if platform.system() == 'Windows':
            wd = webdriver.Chrome('chromedriver', chrome_options=options)
        else:
            wd = webdriver.Chrome('%s/chromedriver' % (os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))), chrome_options=options)

        return wd

    def Start(self, do_background=False):
        self.wd = self.getWebDriver(do_background)

    def Finish(self):
        self.wd.quit()

    def setGroupSelectBox(self):
        setting_done = False
        while setting_done == False:
            setting_done = True
            try:
                if self.country == 'KR':
                    if self.group == 'KOSPI 200':
                        group_type = self.wd.find_element_by_xpath('//*[@id="37427"]')
                    elif self.group == 'KOSDAQ 150':
                        group_type = self.wd.find_element_by_xpath('//*[@id="980241"]')
                elif self.country == 'US':
                    if self.group == 'S&P 500':
                        group_type = self.wd.find_element_by_xpath('//*[@id="166"]')
                    elif self.group == 'Nasdaq 100':
                        group_type = self.wd.find_element_by_xpath('//*[@id="20"]')
                    elif self.group == 'NASDAQ Composite':
                        group_type = self.wd.find_element_by_xpath('//*[@id="14958"]')
                    elif self.group == 'United States all stocks':
                        group_type = self.wd.find_element_by_xpath('//*[@id="all"]')
                group_type.click()
                time.sleep(0.1)
            except (common.exceptions.ElementClickInterceptedException):
                setting_done = False
            except (common.exceptions.NoSuchElementException):
                setting_done = False
        '''
        body = self.wd.find_element_by_css_selector('body')
        for i in range(10):
            body.send_keys(Keys.PAGE_DOWN)
            time.sleep(1)
        '''

    def readCompsTable(self):
        table_done = False
        while table_done == False:
            try:
                html = self.wd.page_source
                bs = BeautifulSoup(html, 'html.parser')
                tables = bs.find('table', {'id': 'cross_rate_markets_stocks_1'}).find('tbody')
                table_done = True if len(tables) > 0 else False
            except (AttributeError):
                table_done = False

        return tables

    def setGroupCountry(self, index_nm):
        self.group = index_nm
        self.country = group_country_dict[index_nm]

    def GetCompListInIndex(self, index_nm, columns):
        self.setGroupCountry(index_nm)
        self.wd.get(self.country_equity_dir[self.country])
        time.sleep(0.1)

        removeAd(self.wd)

        # 그룹내 기들의 기본 데이터를 출력
        df = pd.DataFrame(columns=columns)

        self.setGroupSelectBox()

        data_list = self.readCompsTable()
        for idx_data, data in enumerate(data_list):

            pid = data['id'].split('_')[1]
            nm = data.find('a')['title']
            comp_sub_dir = data.find('a')['href']
            #print(str(idx_data) + '\t' + pid + '\t' + nm + '\t' + comp_sub_dir)
            # continue

            last = data.find('td', {'class': 'pid-%s-last' % (pid)}).text
            high = data.find('td', {'class': 'pid-%s-high' % (pid)}).text
            low = data.find('td', {'class': 'pid-%s-low' % (pid)}).text
            pcp = data.find('td', {'class': 'pid-%s-pcp' % (pid)}).text
            turnover = data.find('td', {'class': 'pid-%s-turnover' % (pid)}).text

            # 교차상장된 종목의 경우 주소 생성 방법이 다름
            p = comp_sub_dir.find('?')
            if p == -1:
                comp_sub_dir_pre = comp_sub_dir
                comp_sub_dir_post = ''
            else:
                comp_sub_dir_pre = comp_sub_dir[:p]
                comp_sub_dir_post = comp_sub_dir[p:]

            comp_dir = self.root_dir + comp_sub_dir_pre + comp_sub_dir_post
            comp_profile_url = self.root_dir + comp_sub_dir_pre + self.profile_sub + comp_sub_dir_post
            comp_financial_url = self.root_dir + comp_sub_dir_pre + self.financial_sub + comp_sub_dir_post
            comp_earnings_url = self.root_dir + comp_sub_dir_pre + self.earnings_sub + comp_sub_dir_post
            comp_dividends_url = self.root_dir + comp_sub_dir_pre + self.dividends_sub + comp_sub_dir_post
            comp_price_url = self.root_dir + comp_sub_dir_pre + self.price_sub + comp_sub_dir_post

            df.loc[idx_data] = [pid, self.country, nm, None, None, None, None, comp_dir, comp_profile_url, comp_financial_url, comp_earnings_url, comp_dividends_url, comp_price_url]

        return df

    def GetProfileData(self, url, df):
        self.wd.get('%s' % (url))
        time.sleep(0.1)

        removeAd(self.wd)

        cnt = 0
        page_done = False
        while page_done == False:
            cnt += 1
            html = self.wd.page_source
            bs = BeautifulSoup(html, 'html.parser')
            tbody = bs.find('div', {'class': 'companyProfileHeader'})
            page_done = True if (tbody is not None and len(tbody) > 0) or cnt > 10 else False

        # 시가총액이 작은 기업의 경우 데이터가 없을 수 있음
        if tbody == None:
            return df

        rows = tbody.findAll('div')
        for idx, row in enumerate(rows):
            if idx == 0:
                df['industry'] = row.text.replace('Industry', '')
            elif idx == 1:
                df['sector'] = row.text.replace('Sector', '')
            else:
                break

        df['market'] = bs.find('i', {'class': 'btnTextDropDwn arial_12 bold'}).text
        df['ticker'] = bs.find('meta', {'itemprop': 'tickerSymbol'})['content']

        return df

    def clickPeriodTypeInFinancialSummary(self, type):
        page_done = False
        while page_done == False:
            page_done = True
            try:
                if type == 'a':
                    result = self.wd.find_element_by_xpath('// *[ @ id = "leftColumn"] / div[9] / a[1]')
                elif type == 'q':
                    result = self.wd.find_element_by_xpath('// *[ @ id = "leftColumn"] / div[9] / a[2]')
                result.click()
                time.sleep(0.1)
            except (common.exceptions.NoSuchElementException):
                try:
                    if type == 'a':
                        result = self.wd.find_element_by_xpath('// *[ @ id = "leftColumn"] / div[10] / a[1]')
                    elif type == 'q':
                        result = self.wd.find_element_by_xpath('// *[ @ id = "leftColumn"] / div[10] / a[2]')
                    result.click()
                    time.sleep(0.1)
                except (common.exceptions.ElementClickInterceptedException):
                    page_done = False
            except (common.exceptions.ElementClickInterceptedException):
                page_done = False

            #time.sleep(0.1)

    def readFinancialSummaryTables(self, type):
        cnt = 0
        table_done = False
        while table_done == False:
            cnt += 1
            try:
                html = self.wd.page_source
                bs = BeautifulSoup(html, 'html.parser')
                tables = bs.findAll('table', {'class': 'genTbl openTbl companyFinancialSummaryTbl'})
                table_done = True if len(tables) > 0 else False
            except (AttributeError):
                table_done = False

            if cnt % 10 == 0:
                print('##### clickPeriodTypeInFinancialSummary again #####')
                self.clickPeriodTypeInFinancialSummary(type)
                #table_done = True

        time.sleep(0.1)
        return tables

    def readFinancialData(self, type, select_term_type=True):

        ret_result = {}

        # Financial Summary에 데이터가 없는 경우 pass
        html = self.wd.page_source
        bs = BeautifulSoup(html, 'html.parser')
        ins_body = bs.findAll('div', {'class': 'instrumentSummaryBody'})
        if len(ins_body) == 0:
            return ret_result

        # 처음 열렸을 Financial 페이지 오픈 시 term type이 quaterly로 시작 되어 해당 버튼 클릭 필요 없음
        if select_term_type == True:
            self.clickPeriodTypeInFinancialSummary(type)
        tables = self.readFinancialSummaryTables(type)

        for table in tables:
            header = table.find('thead').findAll('tr')
            dates = header[0].findAll('th')
            key = None
            for idx_col, column in enumerate(dates):
                if idx_col == 0:
                    key = column.text
                    ret_result[key] = []
                else:
                    ret_result[key].append(column.text)

            if len(header) > 1:
                terms = header[1].findAll('td')
                key = None
                for idx_col, column in enumerate(terms):
                    if idx_col == 0:
                        key = column.text
                        ret_result[key] = []
                    else:
                        ret_result[key].append(column.text)

            tbodys = table.find('tbody').findAll('tr')
            for tbody in tbodys:
                value = tbody.findAll('td')
                key = None
                for idx_col, column in enumerate(value):
                    if idx_col == 0:
                        key = column.text
                        ret_result[key] = []
                    else:
                        ret_result[key].append(column.text)

        for idx_cal, cal in enumerate(ret_result['Period Ending:']):
            cal = cal.replace(',', '').split()
            ret_result['Period Ending:'][idx_cal] = str(date(int(cal[2]), calendar_map[cal[0]], int(cal[1])))

        for idx_cal, cal in enumerate(ret_result['Period Length:']):
            ret_result['Period Length:'][idx_cal] = int(cal.replace(' Months', ''))

        return ret_result

    def GetFinancialData(self, url):
        self.wd.get('%s' % (url))
        time.sleep(0.1)

        removeAd(self.wd)

        # Quarterly 데이터
        quaterly_result = self.readFinancialData(type='q', select_term_type=False)

        # Annual 데이터
        annual_result = self.readFinancialData(type='a', select_term_type=True)

        return {'annual': pd.DataFrame(annual_result), 'quaterly': pd.DataFrame(quaterly_result)}

    def readEarningTable(self):
        cnt = 0
        table_done = False
        while table_done == False:
            cnt += 1
            try:
                html = self.wd.page_source
                bs = BeautifulSoup(html, 'html.parser')
                tbody = bs.find('table', {'class': 'genTbl openTbl ecoCalTbl earnings earningsPageTbl'}).find('tbody')
                rows = tbody.findAll('tr')
                table_done = True if len(rows) > 0 else False
            except (AttributeError):
                table_done = False

            if cnt > 10:
                table_done = True
                rows = []

        time.sleep(0.1)
        return rows

    def GetEarningsData(self, url, loop_num=0):
        self.wd.get('%s' % (url))
        time.sleep(0.3)

        removeAd(self.wd)

        results = []
        loop_cnt = 0
        while 1:
            try:
                # 정해진 횟수만 크롤링
                if loop_cnt >= loop_num:
                    raise Exception('loop_cnt: %s' % (loop_cnt))

                result = self.wd.find_element_by_xpath('//*[@id="showMoreEarningsHistory"]')
                result.click()
                time.sleep(0.3)
                loop_cnt += 1
            except (common.exceptions.ElementClickInterceptedException):
                pass
            except (common.exceptions.NoSuchElementException, Exception):
                #time.sleep(0.1)

                rows = self.readEarningTable()
                for row in rows:
                    release_date = row['event_timestamp']

                    tmp_tbl = row.findAll('td')
                    period_end = tmp_tbl[1].text
                    eps_bold = getRealValue(tmp_tbl[2].text)
                    eps_fore = getRealValue(tmp_tbl[3].text.split('/')[1])
                    revenue_bold = getRealValue(tmp_tbl[4].text)
                    revenue_fore = getRealValue(tmp_tbl[5].text.split('/')[1])

                    results.append({'release_date': release_date, 'period_end': period_end
                                       , 'eps_bold': eps_bold[0]*eps_bold[1], 'eps_fore': eps_fore[0]*eps_fore[1]
                                       , 'revenue_bold': revenue_bold[0]*revenue_bold[1], 'revenue_fore': revenue_fore[0]*revenue_fore[1]})

                return pd.DataFrame(results)

    def readDividendTable(self):
        cnt = 0
        table_done = False
        while table_done == False:
            cnt += 1
            try:
                html = self.wd.page_source
                bs = BeautifulSoup(html, 'html.parser')
                tbody = bs.find('table', {'class': 'genTbl closedTbl dividendTbl'}).find('tbody')
                rows = tbody.findAll('tr')
                table_done = True if len(rows) > 0 else False
            except (AttributeError):
                table_done = False

            if cnt > 10:
                table_done = True
                rows = []

        time.sleep(0.1)
        return rows

    def GetDividendsData(self, url, loop_num=0):
        self.wd.get('%s' % (url))
        time.sleep(0.3)

        removeAd(self.wd)

        results = []
        loop_cnt = 0
        while 1:
            try:
                # 정해진 횟수만 크롤링
                if loop_cnt >= loop_num:
                    raise Exception('loop_done: %s' % (loop_cnt))

                result = self.wd.find_element_by_xpath('//*[@id="showMoreDividendsHistory"]')
                result.click()
                time.sleep(0.3)
                loop_cnt += 1
            except (common.exceptions.ElementClickInterceptedException):
                pass
            except (common.exceptions.NoSuchElementException, Exception):
                try:
                    rows = self.readDividendTable()
                    for row in rows:
                        tmp_tbl = row.findAll('td')
                        ex_date = tmp_tbl[0].text.replace(',', '').split()
                        ex_date = str(date(int(ex_date[2]), calendar_map[ex_date[0]], int(ex_date[1])))
                        dividend = getRealValue(tmp_tbl[1].text)
                        period = tmp_tbl[2].find('span')['title']
                        payment_date = tmp_tbl[3].text.replace(',', '').split()
                        payment_date = str(date(int(payment_date[2]), calendar_map[payment_date[0]], int(payment_date[1])))
                        rate = getRealValue(tmp_tbl[4].text)

                        results.append({'ex_date': ex_date, 'dividend': round(dividend[0]*dividend[1], 4)
                                           , 'period': period, 'payment_date': payment_date
                                           , 'yield': round(rate[0]*rate[1], 4)})
                except:
                    print('No dividends Data.')

                return pd.DataFrame(results)

    def setPeriod(self, start_date, end_date):
        period_done = False
        while period_done == False:
            period_done = True
            try:
                calendar = self.wd.find_element_by_xpath('//*[@id="picker"]')
                self.wd.execute_script("arguments[0].value = '%s - %s';" % (start_date, end_date), calendar)
                self.wd.find_element_by_xpath('//*[@id="widget"]').click()
                time.sleep(0.1)
            except (common.exceptions.ElementClickInterceptedException):
                period_done = False
            #time.sleep(0.1)

    def clikcPeriodBtn(self, start_date, end_date):
        cnt = 0
        btn_done = False
        while btn_done == False:
            btn_done = True
            try:
                button = self.wd.find_element_by_xpath('//*[@id="applyBtn"]')
                self.wd.execute_script("arguments[0].click();", button)
                time.sleep(0.1)
            except (common.exceptions.ElementClickInterceptedException):
                btn_done = False
            except (common.exceptions.NoSuchElementException):
                btn_done = False

            cnt += 1
            if cnt % 10 == 0:
                print('##### setPeriod again #####')
                self.setPeriod(start_date, end_date)

    def readPriceTables(self, start_date, end_date):
        cnt = 0
        table_done = False
        while table_done == False:
            cnt += 1
            try:
                html = self.wd.page_source
                bs = BeautifulSoup(html, 'html.parser')
                tbody = bs.find('table', {'class': 'genTbl closedTbl historicalTbl'}).find('tbody')
                tables = tbody.findAll('tr')
                table_done = True if len(tables) > 0 else False
            except (AttributeError):
                table_done = False
            '''
            if cnt % 10 == 0:
                self.setPeriod(start_date, end_date)
                table_done = True
            '''

        time.sleep(0.1)
        return tables

    def GetPriceData(self, url, set_calendar=False, start_date='1/1/2000', end_date='12/31/9999'):
        self.wd.get('%s' % (url))
        time.sleep(0.1)

        removeAd(self.wd)

        if set_calendar == True:
            self.setPeriod(start_date, end_date)
            self.clikcPeriodBtn(start_date, end_date)

        results = []
        rows = self.readPriceTables(start_date, end_date)
        try:
            for row in rows:
                tmp_tbl = row.findAll('td')
                p_date = tmp_tbl[0].text.replace(',', '').split()
                p_date = str(date(int(p_date[2]), calendar_map[p_date[0]], int(p_date[1])))
                price = getRealValue(tmp_tbl[1].text)
                open = getRealValue(tmp_tbl[2].text)
                high = getRealValue(tmp_tbl[3].text)
                low = getRealValue(tmp_tbl[4].text)
                vol = getRealValue(tmp_tbl[5].text)

                results.append({'Date': p_date, 'Price': price[0]*price[1], 'Open': open[0]*open[1]
                                   , 'High': high[0]*high[1], 'Low': low[0]*low[1], 'Vol.': vol[0]*vol[1]})
        except:
            print('No price Data.')

        return pd.DataFrame(results)


class InvestingEconomicEventCalendar():
    def __init__(self, econmic_event_list, db, process_idx=None):
        self.economic_event_list = econmic_event_list
        self.db = db
        self.options = webdriver.ChromeOptions()
        if 0:
            self.options.add_argument('headless')
            #self.options.add_argument('window-size=1920x1080')
            #self.options.add_argument("disable-gpu")
            # 혹은 options.add_argument("--disable-gpu")
        self.options.add_argument("disable-popup-blocking")

        if platform.system() == 'Windows':
            self.wd = webdriver.Chrome('chromedriver', chrome_options=self.options)
        else:
            if process_idx == None:
                self.wd = webdriver.Chrome('%s/chromedriver' % (os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))), chrome_options=self.options)
            else:
                self.wd = webdriver.Chrome('%s/chromedriver %s' % (os.path.abspath(os.path.join(os.path.dirname(__file__), '..')), process_idx), chrome_options=self.options)

        self.wd.get('https://www.investing.com')
        #time.sleep(5)
        time.sleep(0.1)

        removeAd(self.wd)

    def Start(self, t_gap=0.2, loop_num=float('inf')):
        startTime = timeit.default_timer()

        for data in self.economic_event_list.iterrows():
            cd = data[1]['cd']
            nm = data[1]['nm_us']
            link = data[1]['link']
            ctry = data[1]['ctry']
            period = data[1]['period']
            type = data[1]['type']

            # 배치가 중간에 중단된 경우 문제가 발생한 Event 이후부터 시작
            if cd < 0:
                # if cd not in (81,228,303,331,461,484,569,596,868,889,914,1037,1038,1040,1315,1468,1524,1526,1533,1534,1548,1571,1581,1650,1746,1747,1748,1751,1755,1762,1763,1765,1771,1772,1777,1793,1801,1810,1811,1812,1813,1820,1821,1878,1887,1913):
                print('continue: ', nm, link)
                continue

            # Event별 Schedule 리스트 크롤링
            cralwing_nm, results = self.GetEventSchedule(link, cd, t_gap, loop_num)
            print(cd, nm, cralwing_nm, link, len(results))

            type_in_nm = 'Ori'
            if 'WoW' in cralwing_nm:
                type_in_nm = 'WoW'
            elif 'MoM' in cralwing_nm:
                type_in_nm = 'MoM'
            elif 'QoQ' in cralwing_nm:
                type_in_nm = 'QoQ'
            elif 'YoY' in cralwing_nm:
                type_in_nm = 'YoY'

            # 크롤링된 Event 이름으로 변경
            if nm != cralwing_nm or type != type_in_nm:
                sql = "UPDATE economic_events" \
                      "   SET nm_us='%s'" \
                      "     , type='%s'" \
                      " WHERE cd=%s"
                sql_arg = (cralwing_nm, type_in_nm, cd)
                print(sql % sql_arg)
                if (self.db.execute_query(sql, sql_arg) == False):
                    #print(sql % sql_arg) # update 에러 메세지를 보여준다.
                    pass
            # print(results)

            pre_statistics_time = 0
            # 시계역 역순(가장 최근 데이터가 처음)
            for cnt, result in enumerate(results):
                try:
                    date_rlt = result['date']
                    date_splits = re.split('\W+', date_rlt)
                    date_str = str(date(int(date_splits[2]), calendar_map[date_splits[0]], int(date_splits[1])))

                    # 통계시점에 대한 정보가 없는 경우 주기가 monthly인 경우 처리
                    statistics_time = 'NULL' if len(date_splits) <= 3 or date_splits[3] not in calendar_map.keys() else \
                        calendar_map[date_splits[3]]
                    if period == 'M':
                        # 첫 데이터인 경우 이전달의 값을 역으로 추정
                        if pre_statistics_time == 0:
                            pre_statistics_time = statistics_time + 1 if statistics_time < 12 else 1

                        # 통계시점에 대한 정보가 없는 경우에 이전 데이터에 대한 정보를 사용해서 추정
                        if statistics_time == 'NULL':
                            statistics_time = pre_statistics_time - 1 if pre_statistics_time > 1 else 12

                        pre_statistics_time = statistics_time

                    time = result['time']
                    # GDP처럼 추정치가 먼저 발표되는 경우
                    pre_release_yn = result['pre_release_yn']

                    bold = result['bold']
                    fore = result['fore']
                    prev = result['prev']

                    # 단위가 K, M, %으로 다양하여 실제 수치로 변경
                    bold_value, bold_unit = getRealValue(result['bold'])
                    bold_flt = bold_value * bold_unit if bold_value != 'NULL' or bold_unit != 'NULL' else 'NULL'
                    fore_value, fore_unit = getRealValue(result['fore'])
                    fore_flt = fore_value * fore_unit if fore_value != 'NULL' or fore_unit != 'NULL' else 'NULL'
                    #print(cd, '\t', date_str, '\t', bold_unit)

                    sql = "INSERT INTO economic_events_schedule (event_cd, release_date, release_time, statistics_time, bold_value, fore_value, pre_release_yn, create_time, update_time) " \
                          "VALUES (%s, '%s', '%s', %s, %s, %s, %s, now(), now()) " \
                          "ON DUPLICATE KEY UPDATE release_time = '%s', statistics_time = %s, bold_value = %s, fore_value = %s, pre_release_yn = %s, update_time = now()"
                    sql_arg = (
                        cd, date_str, time, statistics_time, bold_flt, fore_flt, pre_release_yn, time, statistics_time,
                        bold_flt, fore_flt, pre_release_yn)

                    if (self.db.execute_query(sql, sql_arg) == False):
                        # print(sql % sql_arg) # insert 에러 메세지를 보여준다.
                        pass

                except (TypeError, KeyError) as e:
                    print('에러정보 : ', e, file=sys.stderr)
                    print(date_splits, pre_statistics_time)

            endTime = timeit.default_timer()
            print("Cnt:", str(cnt), "\tElapsed time: ", str(endTime - startTime))


    def GetEventSchedule(self, url, cd, t_gap, loop_num):

        self.wd.get(url)
        time.sleep(0.1)

        removeAd(self.wd)

        RESULT_DIRECTORY = '__results__/crawling'
        results = []
        loop_cnt = 0
        while 1:
            try:
                # 정해진 횟수만 크롤링
                if loop_cnt >= loop_num:
                    print(url + '\t' + str(loop_cnt) + '/' + str(loop_num))
                    raise Exception('loop_cnt: ' % loop_cnt)

                script = 'void(0)'  # 사용하는 페이지를 이동시키는 js 코드
                # self.wd.execute_script(script)  # js 실행
                result = self.wd.find_element_by_xpath('//*[@id="showMoreHistory%s"]/a' % cd)
                result.click()
                #self.wd.execute_script("arguments[0].click();", result)
                time.sleep(t_gap)  # 크롤링 로직을 수행하기 위해 5초정도 쉬어준다.

                # body의 contents 업데이트 없이 loop_cnt만 올라가는 것을 막기 위함
                if loop_cnt > 0:
                    html = self.wd.page_source
                    bs = BeautifulSoup(html, 'html.parser')
                    nm = bs.find('body').find('section').find('h1').text.strip()
                    tbody = bs.find('tbody')
                    rows = tbody.findAll('tr')

                    if len(rows) > prev_conts_cnt:
                        loop_cnt += 1
                        prev_conts_cnt = len(rows)

                else:
                    loop_cnt += 1
                    prev_conts_cnt = 0

            except:
                # print('error: %s' % str(page))

                html = self.wd.page_source
                bs = BeautifulSoup(html, 'html.parser')
                nm = bs.find('body').find('section').find('h1').text.strip()
                tbody = bs.find('tbody')
                rows = tbody.findAll('tr')

                for row in rows:
                    tmp_rlt = {}

                    times = row.findAll('td', {'class': 'left'})
                    tmp_rlt['date'] = times[0].text.strip()
                    tmp_rlt['time'] = times[1].text.strip()
                    tmp_rlt['pre_release_yn'] = 1 if times[1].find('span') != None and times[1].find('span')['title'] == "Preliminary Release" else 0

                    values = row.findAll('td', {'class': 'noWrap'})
                    tmp_rlt['bold'] = values[0].text.strip()
                    tmp_rlt['fore'] = values[1].text.strip()
                    tmp_rlt['prev'] = values[2].text.strip()
                    # print(tmp_rlt)

                    results.append(tmp_rlt)

                return nm, results


class IndiceHistoricalData():

    def __init__(self, API_url):
        self.API_url = API_url

        # set https header parameters
        headers = {
            'User-Agent': 'Mozilla/5.0',  # required
            'referer': "https://www.investing.com",
            'host': 'www.investing.com',
            'X-Requested-With': 'XMLHttpRequest'
        }
        self.headers = headers

    # set indice data (indices.py)
    def setFormData(self, data):
        self.data = data

    # prices frequency, possible values: Monthly, Weekly, Daily
    def updateFrequency(self, frequency):
        self.data['frequency'] = frequency

    # desired time period from/to
    def updateStartingEndingDate(self, startingDate, endingDate):
        self.data['st_date'] = startingDate
        self.data['end_date'] = endingDate

    # possible values: 'DESC', 'ASC'
    def setSortOreder(self, sorting_order):
        self.data['sort_ord'] = sorting_order

    # making the post request
    def downloadData(self):
        self.response = requests.post(self.API_url, data=self.data, headers=self.headers).content
        # parse tables with pandas - [0] probably there is only one html table in response
        self.observations = pd.read_html(self.response)[0]
        return self.observations

    # print retrieved data
    def printData(self):
        print(self.data)
        print(self.observations)

    # print retrieved data
    def saveDataCSV(self):
        self.observations.to_csv(self.data['name'] + '.csv', sep='\t', encoding='utf-8')
