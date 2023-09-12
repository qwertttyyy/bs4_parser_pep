# from pprint import pprint
# from urllib.parse import urljoin
#
# from bs4 import BeautifulSoup
# from requests_cache import CachedSession
#
# from src.configs import configure_logging
# from src.constants import PEP_0_URL
# from src.outputs import file_output
# from src.utils import get_response, unexpected_status_logging
#
#
# status_letters = {
#     'A': ['Active', 'Accepted'],
#     'D': 'Deferred',
#     'F': 'Final',
#     'P': 'Provisional',
#     'R': 'Rejected',
#     'S': 'Superseded',
#     'W': 'Withdrawn',
#     'empty': ['Draft', 'Active'],
# }
#
# configure_logging()
# statuses_count = {
#     'Deferred': 0,
#     'Draft': 0,
#     'Withdrawn': 0,
#     'Active': 0,
#     'Provisional': 0,
#     'Accepted': 0,
#     'Final': 0,
#     'Superseded': 0,
#     'Rejected': 0,
# }
#
# session = CachedSession()
# pep_0_page = get_response(session, PEP_0_URL)
# soup = BeautifulSoup(pep_0_page.text, features='lxml')
# section = soup.find('section', id='numerical-index')
# tbody = section.find('tbody')
# rows = tbody.find_all('tr')
#
# for row in rows:
#     type_and_status = row.find('abbr').text
#     pep_card_url = urljoin(PEP_0_URL, row.find('a')['href'])
#
#     pep_card_page = get_response(session, pep_card_url)
#     soup = BeautifulSoup(pep_card_page.text, features='lxml')
#     def_list = soup.find('dl', class_='rfc2822 field-list simple')
#     status_term = def_list.find(
#         lambda tag: tag.name == "dt" and "Status:" in tag.text
#     )
#     status = status_term.find_next('dd').find('abbr').text
#
#     if status in statuses_count:
#         statuses_count[status] += 1
#
#     if len(type_and_status) == 1:
#         if status not in status_letters['empty']:
#             unexpected_status_logging(
#                 pep_card_url, status, status_letters['empty']
#             )
#
#     elif len(type_and_status) == 2:
#         full_status = status_letters[type_and_status[1]]
#         if status != full_status and status not in full_status:
#             unexpected_status_logging(pep_card_url, status, full_status)
#
# results = [('Статус', 'Количество')]
# results.extend((item[0], item[1]) for item in statuses_count.items())
# results.append(('Total', len(rows)))
# file_output(results, '')
