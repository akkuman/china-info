import requests
import urllib
from lxml import etree
import random
import string
import re
import json

class ChinazInfo:
    def get_beian_info(self, domain: str):
        beian_info = {}
        url = 'http://icp.chinaz.com/info?q=' + domain
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
        return beian_info

    def get_beian_relation(self, domain: str):
        results = []
        randstr = ''.join(random.choices(string.ascii_letters, k=16))
        url = 'http://icp.chinaz.com/ajaxsync.aspx?at=beiansl&callback={randstr}&host={host}&type=host'.format(randstr=randstr, host=domain)
        beian_relation_jsonp = requests.get(url).text
        matchs = re.findall(r'SiteLicense:"(.+?)",SiteName:"(.+?)",Owner:".+?",MainPage:"(.+?)",VerifyTime:"(.+?)"', beian_relation_jsonp)
        if not matchs:
            return results
        for match in matchs:
            results.append({
                '备案/许可证号': match[0],
                '网站名称': match[1],
                '网站首页网址': match[2],
                '审核通过时间': match[3],
            })
        return results

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
            'relation': self.get_beian_relation(domain),
        }


if __name__ == "__main__":
    chinaz = ChinazInfo()
    print(chinaz.get_beian('dbappsecurity.com.cn'))