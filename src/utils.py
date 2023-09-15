import logging

from bs4 import BeautifulSoup
from requests import RequestException

from exceptions import ParserFindTagException


def get_response(session, url):
    try:
        response = session.get(url)
        response.encoding = 'utf8'
        return response
    except RequestException:
        logging.exception(
            f'Возникла ошибка при загрузке страницы {url}', stack_info=True
        )


def find_tag(soup, tag, attrs=None):
    search_tag = soup.find(tag, attrs=(attrs or {}))
    if search_tag is None:
        error_msg = f'Не найден тег {tag} {attrs}'
        logging.error(error_msg, stack_info=True)
        raise ParserFindTagException(error_msg)
    return search_tag


def unexpected_status_logging(url, card_status, expected_status):
    logging.info(
        f'{url}\n'
        f'Статус в карточке: {card_status}\n'
        f'Ожидаемые статусы {expected_status}'
    )


def get_soup(session, url):
    response = get_response(session, url)

    if response is None:
        return

    return BeautifulSoup(response.text, features='lxml')
