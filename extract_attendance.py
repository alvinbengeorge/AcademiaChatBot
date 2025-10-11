from bs4 import BeautifulSoup

def extract_attendance(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    attendance_table, marks_table = soup.find_all('table')[4:6]
    attendance_data, marks_data = [], []
    for i, row in enumerate(list(attendance_table.tbody.children)[3:-1]):
        print(i, row)
        cols = list(row.children)
        code_text = cols[0].get_text(strip=True)
        font_tag = cols[0].find("font").get_text(strip=True)
        attendance_dict = {
            "code": code_text.replace(font_tag, "") if font_tag else code_text,
            "type": font_tag if font_tag else "",
            "subject": cols[1].get_text(strip=True),
            "category": cols[2].get_text(strip=True),
            "faculty": cols[3].get_text(strip=True),
            "slot": cols[4].get_text(strip=True),
            "room": cols[5].get_text(strip=True),
            "total_classes": int(cols[6].get_text(strip=True)),
            "hours_absent": int(cols[7].get_text(strip=True)),
            "attendance_percentage": float(cols[8].get_text(strip=True)),
        }
        attendance_data.append(attendance_dict)
    print(marks_table)
    for row in marks_table.tbody.find_all("tr")[1:]:
        cols = row.find_all("td")
        if len(cols) >= 3:  # Make sure we have at least 3 columns
            course_code = cols[0].get_text(strip=True)
            course_type = cols[1].get_text(strip=True)
            
            # Skip if this doesn't look like a proper course code (should start with numbers/letters, not contain slashes)
            if not course_code or '/' in course_code or len(course_code) < 5:
                continue
                
            test_performance = []
            inner_table = cols[2].find("table")
            if inner_table and inner_table.tbody:
                # Get all td elements within the inner table
                test_cells = inner_table.tbody.find_all("td")
                
                for test_cell in test_cells:
                    font_tag = test_cell.find("font")
                    if font_tag:
                        # Extract the test name and max marks from the strong tag
                        strong_tag = font_tag.find("strong")
                        if strong_tag:
                            test_info = strong_tag.get_text(strip=True)
                            # Parse test name and max marks (e.g., "FT-II/15.00")
                            if "/" in test_info:
                                test_name, max_marks = test_info.split("/", 1)
                            else:
                                test_name, max_marks = test_info, ""
                            
                            # Get the score by looking at the text after <br/> tag
                            # Split by the strong tag content and take what comes after
                            font_html = str(font_tag)
                            if "<br/>" in font_html:
                                # Extract everything after the <br/> tag
                                after_br = font_html.split("<br/>", 1)[1]
                                # Remove any remaining HTML tags and get clean text
                                score_soup = BeautifulSoup(after_br, 'html.parser')
                                score_text = score_soup.get_text(strip=True)
                            else:
                                # Fallback: get text and remove the test_info part
                                full_text = font_tag.get_text(strip=True)
                                score_text = full_text.replace(test_info, "").strip()
                            
                            test_performance.append({
                                "test_name": test_name,
                                "max_marks": max_marks,
                                "score": score_text if score_text else "N/A"
                            })
            marks_data.append({
                "course_code": course_code,
                "course_type": course_type,
                "test_performance": test_performance
            })
    return attendance_data, marks_data



if __name__=="__main__":
    with open("sources/My_Attendance.html", "r") as file:
        html_content = file.read()
    attendance_data, marks_data = extract_attendance(html_content)
    
    print("\n=== ATTENDANCE DATA ===")
    print(attendance_data)
    # for item in attendance_data:
    #     print(f"{item['code']} ({item['type']}): {item['subject']} - {item['attendance_percentage']}%")
    
    print("\n=== MARKS DATA ===")
    print(marks_data)
    # for item in marks_data:
    #     print(f"\n{item['course_code']} ({item['course_type']}):")
    #     for test in item['test_performance']:
    #         print(f"  {test['test_name']}/{test['max_marks']}: {test['score']}")