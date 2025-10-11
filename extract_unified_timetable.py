from bs4 import BeautifulSoup
from pprint import pprint

def extract_unified_timetable(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    table_results = soup.find_all('table')
    timetable_table = table_results[2].tbody
    rows = list(timetable_table.children)
    timings = [{'from': i.get_text().split()[0].strip('-'), 'to': i.get_text().split('-')[1].strip()} for i in list(rows[0].children)[2:] if i and i != '\n']
    timetable_data = []
    for i, row in enumerate(rows[6:], 1):
        # Skip empty rows or non-tag rows
        if not hasattr(row, 'find_all'):
            continue
        cells = row.find_all('td')
        if not cells:
            continue
        day = cells[0].get_text(strip=True)
        periods = []
        for idx, cell in enumerate(cells[1:]):
            period_info = {
            'time': timings[idx] if idx < len(timings) else {},
            'slot': cell.get_text(strip=True)
            }
            periods.append(period_info)
        timetable_data.append({'day': day, 'periods': periods})
    return timetable_data

if __name__ == "__main__":
    with open("sources/Unified_Time_Table_2025_batch_2.html", "r") as file:
        html_content = file.read()
    extract_unified_timetable(html_content)