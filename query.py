from langchain_ollama import OllamaLLM
from langchain_chroma import Chroma
from langchain.prompts import ChatPromptTemplate
from generate_chroma import CHROMA_LOC, get_embedding_functions
import glob
import json
import os

EMBEDDING_FUNCTION = get_embedding_functions()
db = Chroma(
    embedding_function=EMBEDDING_FUNCTION,
    persist_directory=CHROMA_LOC
)

TEMPLATE = """
You are an academic assistant, that contains the data of one single student, and you have to answer questions based on the data, you must also perform calculations if required.
THIS IS THE DATABASE OF A SINGLE STUDENT

SCHEMA:

# 📘 Data Structure Explanation

## 🧾 attendance_data

**Description:**
Contains attendance details for each subject (both theory and practical).

**Fields:**

* **code** – Unique course code (example: 21ECC412J)
* **type** – Type of registration (example: Regular)
* **subject** – Subject name (example: Programming with Python)
* **category** – Theory or Practical
* **faculty** – Name of the faculty handling the subject
* **slot** – Timetable slot (example: A, B, LAB)
* **room** – Room or lab number
* **total_classes** – Total number of classes conducted
* **hours_absent** – Number of classes missed
* **attendance_percentage** – Percentage of attendance for this subject

**Key Relation:**
Linked to `timetable_data` and `marks_data` by **code** or **course_code**.

---

## 🧮 marks_data

**Description:**
Contains test and performance details for each subject.

**Fields:**

* **course_code** – Same as `attendance_data.code` and `timetable_data.course_code`
* **course_type** – Theory or Practical
* **test_performance** – A list containing details of each test:

  * **test_name** – Name of the test (example: FT-I, LLJ-I)
  * **max_marks** – Maximum marks for the test
  * **score** – Marks obtained by the student or "Abs" if absent

**Key Relation:**
Linked to `attendance_data` and `timetable_data` using **course_code**.

---

## 🗓️ timetable_data

**Description:**
Lists all registered courses, their category, slot, and faculty details.

**Fields:**

* **course_code** – Unique course code (same as `attendance_data.code`)
* **course_title** – Full name of the subject
* **credit** – Credit value for the course
* **regn_type** – Type of registration (example: Regular)
* **category** – Course category (example: Professional Core, Elective)
* **course_type** – Whether it's Theory, Lab, or Lab Based Theory
* **faculty_name** – Name of the faculty member
* **slot** – Slot used in the unified timetable (example: A, B, P37-P38-)
* **room_no** – Room or lab location
* **academic_year** – Academic session (example: AY2025-26-ODD)

**Key Relation:**
Links subjects to `unified_time_table` via the **slot**.

---

## 🕒 unified_time_table

**Description:**
Defines the daily and weekly schedule for each slot.

**Fields:**

* **day** – Name of the day (example: Day 1, Day 2, Day 3, etc.)
* **periods** – List of class periods for that day

  * **time (from)** – Start time of the period (example: 08:00)
  * **time (to)** – End time of the period (example: 08:50)
  * **slot** – Slot code for that period (example: A, B, P37)

**Key Relation:**
Each **slot** here corresponds to a **slot** in `timetable_data` to determine the subject and faculty.

---

## 🔗 Data Relationship Summary

| Relationship                        | Description                                                                              |
| ----------------------------------- | ---------------------------------------------------------------------------------------- |
| attendance_data ↔ marks_data        | Connected through course_code or code to compare performance and attendance              |
| attendance_data ↔ timetable_data    | Connected through course_code or code to identify subject and faculty                    |
| timetable_data ↔ unified_time_table | Connected via slot to map subjects to specific time periods in the weekly schedule       |
| Overall                             | All datasets are linked through course_code and slot to form a unified academic overview |

---

Would you like me to add a **short example paragraph** describing how these four datasets work together (like a story explaining how they connect)?


Answer the question based on the following context:
{context}

------------------------------------
Answer the question based on the above context:
{question}

MAKE IT SIMPLE AND DO NOT PROVIDE CODE, JUST ANSWER IN PLAIN TEXT IN ONE OR TWO LINES MAXIMUM
"""

PROMPT_TEMPLATE = ChatPromptTemplate.from_template(TEMPLATE)


def query(text: str):
    context = ""
    for i in os.listdir("structured_data/"):
        with open(f"structured_data/{i}", "r") as f:
            context += f"\n---------------\n{i.capitalize()}:\n" + f.read()


    prompt = PROMPT_TEMPLATE.format(context=context, question=text)
    model = OllamaLLM(model="gemma3:latest")    
    print(context)
    # print(*results, sep="\n")
    response = model.invoke(prompt)
    print(response)

while True:
    text = input("Enter query: ")
    query(text)
