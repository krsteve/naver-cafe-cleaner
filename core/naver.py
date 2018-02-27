from naverlogin import NaverSession

CAFE_LIST_URL = 'https://m.cafe.naver.com/SectionMyCafeListAjax.nhn'


class NaverCafe:
    def __init__(self, cafe_info=None):
        self.club_id = None
        self.name = ''
        self.url = ''
        self.is_favorite = None
        self.user_nickname = ''
        self.last_visited = None
        self.thumbnail_url = ''

        if cafe_info is not None:
            self.feed_info(cafe_info)

    def feed_info(self, cafe_info: dict):
        self.club_id = cafe_info['cafeId']
        self.name = cafe_info['clubName']
        self.url = cafe_info['clubUrl']
        self.is_favorite = cafe_info['favorite']
        self.user_nickname = cafe_info['memberNickname']
        self.last_visited = cafe_info['lastVisitDate']
        self.thumbnail_url = cafe_info['cafeThumbnailImageUrlMobile']

    def __str__(self):
        return 'NaverCafe Object (#{}: {})'.format(self.club_id, self.name)


def get_naver_session(username: str, password: str) -> NaverSession:
    naver = NaverSession()
    if naver.login(username, password):
        return naver
    return


def get_cafe_list_info(naver: NaverSession) -> dict:
    res = naver.post(CAFE_LIST_URL)
    return res.json()


def get_total_pages(cafe_list_info: dict) -> int:
    return cafe_list_info['result']['search']['totalPageCount']


def get_cafe_list_page(naver: NaverSession, page_no: int) -> dict:
    res = naver.post(CAFE_LIST_URL, data={'search.page': page_no})
    return res.json()


def get_cafes(naver: NaverSession):
    cafe_list_info = get_cafe_list_info(naver)
    total_pages = get_total_pages(cafe_list_info)

    cafes_list = []

    for i in range(1, total_pages + 1):
        page = get_cafe_list_page(naver, i)
        page_cafes = page['result']['moreList']
        cafes_list += [NaverCafe(x) for x in page_cafes]

    return cafes_list


def remove_cafe(naver: NaverSession, cafe: NaverCafe):
    url = "https://m.cafe.naver.com/CafeSecede.nhn?clubid=%d" % cafe.club_id
    headers = {
        'Accept': '*/*',
        'Referer': 'https://m.cafe.naver.com/' + cafe.url,
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.167 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
    }
    res = naver.get(url, headers=headers)
    try:
        data = res.json()
        if data['message']['status'] == '200' and data['message']['result']['msg'] == '탈퇴하셨습니다.':
            return True
    except Exception:
        pass
    return False
