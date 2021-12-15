import os
from flask import current_app
from selenium.webdriver.chrome.options import Options
import selenium.common.exceptions
import time
import datetime


root_path = current_app.root_path

with open(os.path.join(root_path, 'secret', 'login_link')) as f:
    _login_link = f.read()
with open(os.path.join(root_path, 'secret', 'data_link')) as f:
    _data_link = f.read()


def get_member_list():
    import pandas as pd
    df = pd.read_excel(os.path.join(root_path, 'secret', 'secret/youth_league_member_list.xls'))
    return set(df['团员列表'][2:])


class DataUpdater:
    _studied_name_list = set()
    _unstudied_name_list = get_member_list()

    _chrome_options = Options()
    _chrome_options.add_argument('--headless')
    _chrome_options.add_argument('--disable-gpu')
    _browser = selenium.webdriver.Chrome(options=_chrome_options)

    def solve(self):
        items = self._browser.find_elements_by_xpath('//table[@class="el-table__body"]/tbody/tr')
        names = [item.text.split('\n')[0] for item in items]
        for name in names:
            self._studied_name_list.add(str(name))
            self._unstudied_name_list.remove(str(name))

    def print_info(self):
        # print(self._studied_name_list)
        print(self._unstudied_name_list)
        print(datetime.date.today())

    def __init__(self, login_link=_login_link, data_link=_data_link):
        self.login_link = login_link
        self.data_link = data_link

    def _login(self):
        self._browser.get(self.login_link)
        time.sleep(5)

    def run(self):
        self._login()
        try:
            self._browser.get(self.data_link)
        except selenium.common.exceptions.InvalidArgumentException:
            print('The link is invalid. Please make sure the link is valid, with leading http or https.')
        time.sleep(5)

        try:
            latest_link = self._browser.find_element_by_xpath(
                '//table[@class="el-table__body"]/tbody/tr/td[5]/div/div'
            )
            latest_link.click()
            time.sleep(5)
        except selenium.common.exceptions.NoSuchElementException:
            print('The link has no such element for crawler to identify. Please check the link.')
            return False

        try:
            # btn_next = browser.find_element_by_xpath('//button[@class="btn-next"]')
            btn_next = self._browser.find_element_by_xpath(
                '//div[@class="pagination-container"]/div/button[@class="btn-next"]')
            while btn_next.get_attribute('disabled') is None:
                self.solve()
                btn_next.click()
                time.sleep(5)
            self.solve()
            self.print_info()
            return True
        except selenium.common.exceptions.NoSuchElementException:
            print('The link has no such element for crawler to identify. Please check the link.')
            return False

    def check_user(self, real_name):
        return real_name in self._studied_name_list

    def quit(self):
        self._browser.quit()


def test():
    data_updater = DataUpdater(_login_link, _data_link)
    data_updater.run()
    data_updater.quit()


# test()

if __name__ == '__main__':
    test()
