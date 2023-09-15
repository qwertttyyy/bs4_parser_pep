import logging
import re
from collections import defaultdict
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from requests_cache import CachedSession
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import MAIN_DOC_URL, BASE_DIR, PEP_0_URL, EXPECTED_STATUS
from outputs import control_output
from exceptions import ParserFindTagException
from utils import get_response, find_tag, unexpected_status_logging, get_soup


def whats_new(session):
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    soup = get_soup(session, whats_new_url)

    if soup is None:
        return
    main_div = find_tag(soup, 'section', {'id': 'what-s-new-in-python'})
    div_with_url = find_tag(main_div, 'div', {'class': 'toctree-wrapper'})
    sections_by_python = div_with_url.find_all(
        'li', attrs={'class': 'toctree-l1'}
    )

    results = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]
    for section in tqdm(sections_by_python):
        version_a_tag = find_tag(section, 'a')
        href = version_a_tag['href']
        version_link = urljoin(whats_new_url, href)
        soup = get_soup(session, version_link)

        if soup is None:
            continue

        h1 = find_tag(soup, 'h1')
        dl = find_tag(soup, 'dl')
        dl_text = dl.text.replace('\n', ' ')
        results.append((version_link, h1.text, dl_text))

    return results


def latest_versions(session):
    soup = get_soup(session, MAIN_DOC_URL)

    if soup is None:
        return

    side_bar = find_tag(soup, 'div', {'class': 'sphinxsidebarwrapper'})
    ul_tags = side_bar.find_all('ul')

    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        raise ParserFindTagException('Ничего не нашлось')

    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    for a_tag in a_tags:
        link = a_tag['href']
        string = re.search(pattern, a_tag.text)
        if string:
            version, status = string.groups()
        else:
            version = a_tag.text
            status = ''

        results.append((link, version, status))

    return results


def download(session):
    download_url = urljoin(MAIN_DOC_URL, 'download.html')
    soup = get_soup(session, download_url)

    if soup is None:
        return

    main_tag = find_tag(soup, 'div', {'role': 'main'})
    table_tag = find_tag(main_tag, 'table', {'class': 'docutils'})
    pdf_a4_tag = find_tag(
        table_tag, 'a', {'href': re.compile(r'.+pdf-a4\.zip$')}
    )
    pdf_a4_tag = pdf_a4_tag['href']
    archive_url = urljoin(download_url, pdf_a4_tag)

    filename = archive_url.split('/')[-1]

    downloads_dir = BASE_DIR / 'downloads'
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename

    response = session.get(archive_url)

    with open(archive_path, 'wb') as file:
        file.write(response.content)

    logging.info(f'Архив был загружен и сохранён: {archive_path}')


def pep(session):
    soup = get_soup(session, PEP_0_URL)

    if soup is None:
        return

    section = find_tag(soup, 'section', {'id': 'numerical-index'})
    tbody = find_tag(section, 'tbody')
    rows = tbody.find_all('tr')

    statuses_count = defaultdict(int)

    for row in rows:
        type_and_status = find_tag(row, 'abbr').text
        pep_card_url = urljoin(PEP_0_URL, row.find('a')['href'])
        soup = get_soup(session, pep_card_url)

        if soup is None:
            return

        def_list = find_tag(soup, 'dl', {'class': 'rfc2822 field-list simple'})
        status_term = find_tag(
            def_list, lambda tag: tag.name == "dt" and "Status:" in tag.text
        )
        status = status_term.find_next('dd').find('abbr').text

        statuses_count[status] += 1

        if len(type_and_status) == 1:
            if status not in EXPECTED_STATUS['empty']:
                unexpected_status_logging(
                    pep_card_url, status, EXPECTED_STATUS['empty']
                )

        elif len(type_and_status) == 2:
            full_status = EXPECTED_STATUS[type_and_status[1]]
            if status != full_status and status not in full_status:
                unexpected_status_logging(pep_card_url, status, full_status)

    results = [('Статус', 'Количество')]
    results.extend((item[0], item[1]) for item in statuses_count.items())
    results.append(('Total', len(rows)))

    return results


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep,
}


def main():
    configure_logging()
    logging.info('Парсер запущен!')
    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logging.info(f'Аргументы командной строки: {args}')

    session = CachedSession()

    if args.clear_cache:
        session.cache.clear()

    parser_mode = args.mode
    try:
        results = MODE_TO_FUNCTION[parser_mode](session)
        if results is not None:
            control_output(results, args)
    except Exception:
        error_msg = f'Ошибка при выполнении с аргументом {parser_mode}'
        logging.error(error_msg, stack_info=True)

    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
