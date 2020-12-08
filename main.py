import time

from bs4 import BeautifulSoup
import requests


class TabelogScraping:
    """
    食べログから東京でのデートで使えるお店トップ10の情報を取得する。
    情報は「店名」「評価」「エリア・ジャンル」「URL」「最新口コミ1件」である。
    """
    def __init__(self):
        """
        インスタンス化した時点でスクレイピングを開始する
        食べログ（検索条件：東京都、デート、ランキング順）にアクセスする
        取得する情報はベスト10までとする。
        """
        # 口コミURLの不足部分
        self.RVW = 'dtlrvwlst/'

        try:
            first_time = time.time()
            # スクレイピング対象の URL にリクエストを送り HTML を取得する
            res = requests.get('https://tabelog.com/tokyo/rstLst/cond52-00-00/'
                               '?SrtT=rt&LstSmoking=0&ChkCoupleSeat=1&svd=202'
                               '01204&svt=1900&svps=2&Srt=D&sort_mode=1')

            # レスポンスの HTML から BeautifulSoup オブジェクトを作る
            soup = BeautifulSoup(res.text, 'html.parser')

            # 店名と店のURLの取得
            raw_data = soup.find_all('a',
                                     class_='list-rst__rst-name-target cpy-rst'
                                            '-name js-ranking-num',
                                     limit=10)
            shop_list = [name.text for name in raw_data]
            shop_url_list = [shop_url.get('href') for shop_url in raw_data]

            # 評価点の取得
            rate_list = \
                [float(rate.text) for rate in soup.find_all
                 ('span',
                  class_='c-rating__val c-rating__val--strong list-'
                  'rst__rating-val',
                  limit=10)]

            # エリアとジャンルの取得
            genre_info = [genre.text.rstrip() for genre in soup.find_all(
                'div',
                class_='list-rst__area-genre cpy-area-genre',
                limit=10)]

            reviews = []
            # お店のURLに遷移し、口コミを取得する
            for url in shop_url_list:
                response = self.connect_url(url + self.RVW)
                soup = BeautifulSoup(response.text, 'lxml')
                review_url_list = soup.find_all('div',
                                                class_='rvw-item js-rvw-item'
                                                '-clickable-area',
                                                limit=1)
                # 各口コミページに遷移し、最新の口コミを取得する
                for url in review_url_list:
                    review_detail_url = 'https://tabelog.com' + \
                        url.get('data-detail-url')
                    response = self.connect_url(review_detail_url)
                    soup = BeautifulSoup(response.text, 'lxml')
                    review = soup.find_all('div',
                                           class_='rvw-item__rvw-comment',
                                           limit=1)
                    review = review[0].p.text.strip()
                    reviews.append(review)

            # それぞれのデータを出力する
            for i, shop, rate, genre, url, rev in zip(range(10), shop_list,
                                                      rate_list, genre_info,
                                                      shop_url_list, reviews):
                print('{}位「{}」 評価{} {}\nURL {}\n{}\n'.format(i+1, shop, rate,
                      genre, url, rev))

        except requests.exceptions.HTTPError as e:
            print(e)
        except requests.exceptions.ConnectTimeout as e:
            print(e)
        finally:
            end_time = time.time() - first_time
            print('終了、処理時間：{:.3f}秒'.format(end_time))

    def connect_url(self, target_url):
        """
        対象のURLにアクセスする関数
        アクセスできない等のエラーが発生したら例外を投げる
        """
        # 接続確立の待機時間、応答待機時間を15秒とし、それぞれの値を超えた場合は例外が発生（ConnectTimeout）
        data = requests.get(target_url, timeout=15)
        data.encoding = data.apparent_encoding
        # アクセス過多を避けるため、2秒スリープ
        time.sleep(2)
        # レスポンスのステータスコードが正常(200番台)以外の場合は、例外を発生させる(HTTPError)
        if data.status_code == 200:
            return data
        else:
            data.raise_for_status()


if __name__ == '__main__':
    result = TabelogScraping()
    print(result)
