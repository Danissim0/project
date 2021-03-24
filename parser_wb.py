
"""
Сейчас занимаюсь переписыванием парсеров на Java и созданием интерфейса, а также запросами пользователя
"""

import logging
import collections

import requests
import bs4

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('wb')

ParseResult = collections.namedtuple(
    'ParseResult',
    (
        'brand_name',
        'goods_name',
        'url',
    ),
)

# будет зависеть от запроса пользователя
parse_url = 'https://www.wildberries.ru/catalog/muzhchinam/odezhda/verhnyaya-odezhda'

class Client:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0(Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 YaBrowser/21.2.4.172 Yowser/2.5 Safari/537.36',
            'Accept-Language': 'ru',
        }
        self.result = []

    def load_page(self):
        url = parse_url
        res = self.session.get(url=url)
        res.raise_for_status()
        return res.text

    def parse_page(self, text: str):
        soup = bs4.BeautifulSoup(text, 'lxml')
        container = soup.select('div.dtList.i-dtList.j-card-item')
        for block in container:
            self.parse_block(block=block)

    def parse_block(self, block):
        # logger.info(block)
        # logger.info('=' * 100)

        url_block = block.select_one('a.ref_goods_n_p')
        if not url_block:
            logger.error('no_url_block')
            return

        url = url_block.get('href')
        if not url:
            logger.error('no_url')
            return

        name_block = block.select_one('div.dtlist-inner-brand-name')
        if not name_block:
            logger.error('no_name_block')
            return

        brand_name = name_block.select_one('strong.brand-name')
        if not brand_name:
            logger.error('no_brand_name')
            return
        brand_name = brand_name.text
        brand_name = brand_name.replace('/', '').strip()

        goods_name = name_block.select_one('span.goods-name.c-text-sm')
        if not goods_name:
            logger.error('no_goods_name')
            return
        goods_name = goods_name.text.strip()

        logger.debug('%s %s %s', url, brand_name, goods_name)

        self.result.append(ParseResult(
            url=url,
            brand_name=brand_name,
            goods_name=goods_name,
        ))

    def run(self):
        text = self.load_page()
        self.parse_page(text=text)

if __name__ == '__main__':
    parser = Client()
    parser.run()