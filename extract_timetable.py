from bs4 import BeautifulSoup

def extract_timetable(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    timetable_section = soup.find('table', class_='course_tbl')
    timetable_section = timetable_section.tbody
    timetable_data = []
    for i, row in enumerate(list(timetable_section.children)[3:-1]):
        cols = list(row.children)        
        keys = [
            "s_no", "course_code", "course_title", "credit", "regn_type",
            "category", "course_type", "faculty_name", "slot", "room_no", "academic_year"
        ]
        cols = [col.get_text(strip=True) for col in cols if col.name == 'td']
        if cols and len(cols) == len(keys):
            row_dict = dict(zip(keys, cols))
            timetable_data.append(row_dict)
    return timetable_data
    

if __name__ == "__main__":
    with open("sources/My_Time_Table_2023_24.html", "r") as file:
        html_content = file.read()
    print(extract_timetable(html_content))