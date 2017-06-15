import lxml.html as parser
import requests
import csv
from urllib.parse import urlsplit, urljoin


class EcommerceSpider(object):
    def __init__(self, start_url):
        self.links = set()
        self.items = []
        self.start_url = start_url
        self.set_base_url()

    def crawl(self):
        self.get_links()
        self.get_items()

    def crawl_to_file(self, filename):
        self.crawl()
        self.save_items(filename)

    def get_links(self):
        item_url_xpath = "//a[@class='card-product-url']/@href"
        next_page_xpath = "//div[@class='card card-pagination']/a/@href"
        r = requests.get(self.start_url)
        html = parser.fromstring(r.text)
        self.parse_links(html, item_url_xpath)
        next_page = html.xpath(next_page_xpath)[0]
        while next_page:
            r = requests.get(urljoin(self.base_url, next_page))
            html = parser.fromstring(r.text)
            self.parse_links(html, item_url_xpath)
            try:
                next_page = html.xpath(next_page_xpath)[1]
            except IndexError as e:
                next_page = None

    def get_items(self):
        for link in self.links:
            r = requests.get(link)
            html = parser.fromstring(r.text)
            self.items.append(self.extract_item(html, link))

    def extract_item(self, html, link):
        try:
            name = html.xpath("//h1[@class='product-name']/text()")[0]
        except IndexError as e:
            print("Name not found at page %s" % link)
            name = "Not found"

        try:
            price_str = html.xpath("//p[@class='sales-price']/text()")[0]
            price = float(price_str[3:].replace(".", "").replace(",", "."))
        except IndexError as e:
            print("Price not found at page %s" % link)
            price = "Not found"

        return {
            'url': link,
            'name': name,
            'price': price
        }

    def parse_links(self, html, item_url_xpath):
        new_links = html.xpath(item_url_xpath)
        new_links = [self.prepare_url(l) for l in new_links]
        self.links = self.links.union(set(new_links))

    def set_base_url(self):
        self.base_url = urlsplit(self.start_url)._replace(path="", query="").geturl()

    def prepare_url(self, url):
        url = urljoin(self.base_url, url)
        return urlsplit(url)._replace(query="").geturl()

    def save_items(self, filename):
        keys = self.items[0].keys()
        with open(filename, 'w') as f:
            dict_writer = csv.DictWriter(f, keys)
            dict_writer.writeheader()
            dict_writer.writerows(self.items)


spider = EcommerceSpider("https://www.submarino.com.br/busca/?conteudo=moto%20g&filtro=%5B%7B%22id%22%3A%22category_breadcrumb_name_level_pt_suba_1%22%2C%22value%22%3A%22Celulares%20e%20Smartphones%22%7D%2C%7B%22id%22%3A%22category_breadcrumb_name_level_pt_suba_2%22%2C%22value%22%3A%22Moto%20G%22%7D%5D&ordenacao=moreRelevant&origem=nanook")
spider.crawl_to_file("motog.csv")
