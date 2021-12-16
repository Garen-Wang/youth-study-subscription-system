from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import selenium.common.exceptions
import time
import datetime
import pandas as pd

from config import data_link, login_link


def get_member_list(path):
    df = pd.read_excel(path)
    return set(df['团员列表'][2:])


class DataUpdater:
    _chrome_options = Options()
    _chrome_options.add_argument('--headless')
    _chrome_options.add_argument('--disable-gpu')
    _browser = selenium.webdriver.Chrome(options=_chrome_options)

    def solve(self):
        items = self._browser.find_elements(By.XPATH, '//table[@class="el-table__body"]/tbody/tr')
        # items = self._browser.find_elements_by_xpath('//table[@class="el-table__body"]/tbody/tr')
        names = [item.text.split('\n')[0] for item in items]
        for name in names:
            self._studied_name_list.add(str(name))
            self._unstudied_name_list.remove(str(name))

    def print_info(self):
        # print(self._studied_name_list)
        print(self._unstudied_name_list)
        print(datetime.date.today())

    def __init__(self, login_link=login_link, data_link=data_link):
        self.member_list = get_member_list('secret/youth_league_member_list.xls')
        self.login_link = login_link
        self.data_link = data_link
        self._studied_name_list = set()
        self._unstudied_name_list = self.member_list

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
            # latest_link = self._browser.find_element_by_xpath(
            #     '//table[@class="el-table__body"]/tbody/tr/td[5]/div/div'
            # )
            latest_link = self._browser.find_element(By.XPATH, '//table[@class="el-table__body"]/tbody/tr/td[5]/div/div')
            latest_link.click()
            time.sleep(5)
        except selenium.common.exceptions.NoSuchElementException:
            print('The link has no such element for crawler to identify. Please check the link.')
            return False

        try:
            # btn_next = self._browser.find_element_by_xpath(
            #     '//div[@class="pagination-container"]/div/button[@class="btn-next"]')
            btn_next = self._browser.find_element(By.XPATH, '//div[@class="pagination-container"]/div/button[@class="btn-next"]')
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

    @property
    def unstudied_name_list(self):
        return self._unstudied_name_list

    @property
    def studied_name_list(self):
        return self._studied_name_list


def test():
    data_updater = DataUpdater(login_link, data_link)
    data_updater.run()
    data_updater.quit()


def update_studied_list():
    data_updater = DataUpdater(login_link, data_link)
    data_updater.run()
    data_updater.quit()
    return data_updater.studied_name_list


# test()

if __name__ == '__main__':
    test()
