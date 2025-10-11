import json
from pydantic import BaseModel
from pprint import pprint

class AttendanceRecord(BaseModel):
    code: str
    type: str
    subject: str
    category: str
    faculty: str
    slot: str
    room: str
    total_classes: int
    hours_absent: int
    attendance_percentage: float

class TestPerformance(BaseModel):
    test_name: str
    max_marks: str
    score: str

class MarksRecord(BaseModel):
    course_code: str
    course_type: str
    test_performance: list[TestPerformance]

class TimetableRecord(BaseModel):
    academic_year: str
    category: str
    course_code: str
    course_title: str
    course_type: str
    credit: str
    faculty_name: str
    regn_type: str
    room_no: str
    s_no: str
    slot: str

with open("structured_data/attendance_data.json", "r") as f:
    attendance_data = json.load(f)
    # print(attendance_data)

with open("structured_data/marks_data.json", "r") as f:
    marks_data = json.load(f)
    # print(marks_data)

with open("structured_data/timetable_data.json", "r") as f:
    timetable_data = json.load(f)
    pprint(timetable_data)

with open("structured_data/unified_timetable_data.json", "r") as f:
    unified_timetable_data = json.load(f)
    # pprint(unified_timetable_data)

if __name__ == "__main__":
    attendance_data = [AttendanceRecord(**record) for record in attendance_data]
    marks_data = [MarksRecord(**record) for record in marks_data]
    timetable_data = [TimetableRecord(**record) for record in timetable_data]
    
    
    # unified_timetable_data = [TimetableRecord(**record) for record in mapped_unified_data]

