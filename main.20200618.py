import requests
import urllib
from lxml import etree
import random
import string
import re
import json

class ChinazInfo:
    def __init__(self):
        self.beian_main_info = {}
        self.beian_relation_info = {}

    def get_beian_info(self, domain: str):
        beian_info = {}
        url = 'https://icp.chinaz.com/home/info?host=' + domain
        beian_main = requests.get(url)
        html = etree.HTML(beian_main.text)
        # 获取备案信息
        by1_elements = html.xpath('//td[@class="by1"]')
        # 判断是否存在备案
        if by1_elements[0].text.strip() == '--':
            return beian_info
        if len(by1_elements) == 7:
            beian_info['备案/许可证号'] = by1_elements[0].text
            beian_info['主办单位名称'] = by1_elements[1].text
            beian_info['网站名称'] = by1_elements[2].text
            beian_info['网站负责人姓名'] = by1_elements[3].text
            website_a_tag = by1_elements[4].getchildren()[0].getchildren()[0].getchildren()
            if website_a_tag:
                beian_info['网站域名'] = website_a_tag[0].text
            beian_info['网站备案/许可证号'] = by1_elements[5].text
            beian_info['网站前置审批项'] = by1_elements[6].text

        by2_elements = html.xpath('//td[@class="by2"]')
        if len(by2_elements) == 3:
            beian_info['审核通过时间'] = by2_elements[0].text
            beian_info['主办单位性质'] = by2_elements[1].text
            beian_info['网站首页网址'] = by2_elements[2].text
        self.beian_main_info = beian_info
        return self.beian_main_info
    
    def get_same_beian_doamin(self, domain: str):
        results = []
        if not self.beian_main_info:
            self.get_beian_info(domain)
        organizer = self.beian_main_info['主办单位名称'].strip()
        if not organizer:
            self.beian_main_info = results
            return self.beian_main_info
        url = 'https://icp.chinaz.com/Home/PageData'
        page_no = 1
        page_size = 20
        amount = page_no * page_size
        while 1:
            if len(results) == amount or page_no > 10:
                break
            data = {
                'Kw': organizer,
                'pageNo': page_no,
                'pageSize': page_size,
            }
            beian_relation_json = requests.post(url, data=data).json()
            amount = beian_relation_json.get('amount', 0)
            page_no += 1
            for item in beian_relation_json.get('data', []):
                results.append({
                    '备案/许可证号': item['permit'],
                    '网站名称': item['webName'],
                    '网站首页网址': item['host'],
                    '审核通过时间': item['verifyTime'],
                    '负责人': item['owner'],
                    '网站类型': item['typ']
                })
        self.beian_relation_info = results
        return self.beian_relation_info

    def get_beian(self, domain: str):
        """获取备案以及关联备案信息

        Args:
            domain: 站点域名，加不加http均可
        
        Returns:
            备案信息
            example:

            {
                'main': {'备案/许可证号': 'xxx'},
                'relation': [{'备案/许可证号': 'xxx'}]
            }
        """
        domain = domain.strip()
        if domain.startswith('http://') or domain.startswith('https://'):
            domain = urllib.parse.urlparse(domain).netloc
        return {
            'main': self.get_beian_info(domain),
            'relation': self.get_same_beian_doamin(domain),
        }


if __name__ == "__main__":
    chinaz = ChinazInfo()
    print(chinaz.get_beian('baidu.com'))