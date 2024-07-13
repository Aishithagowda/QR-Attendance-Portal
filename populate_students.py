import pandas as pd
import os
import django

# Set the DJANGO_SETTINGS_MODULE environment variable
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'QR_Attendance_System.settings')
django.setup()

from django.contrib.auth.models import User
from FacultyView.models import Branch, Section, Year, Student

# Read user credentials from Excel
user_credentials = pd.read_excel('user_credentials.xlsx')
student_details = pd.read_excel('student_details.xlsx')

# Loop through user credentials and create User objects
for index, row in user_credentials.iterrows():
    username = row['username']
    password = row['password']
    user, created = User.objects.get_or_create(username=username)
    if created:
        user.set_password(password)
        user.save()

# Loop through student details and create Student objects
for index, row in student_details.iterrows():
    username = row['username']
    user = User.objects.get(username=username)
    
    s_roll = row['s_roll']
    s_fname = row['s_fname']
    s_lname = row['s_lname']
    branch_name = row['s_branch']
    section_name = row['s_section']
    year_number = row['s_year']

    branch, _ = Branch.objects.get_or_create(branch=branch_name)
    section, _ = Section.objects.get_or_create(section=section_name)
    year, _ = Year.objects.get_or_create(year=year_number)

    Student.objects.get_or_create(
        user=user,
        s_roll=s_roll,
        s_fname=s_fname,
        s_lname=s_lname,
        s_branch=branch,
        s_section=section,
        s_year=year
    )

print("User and Student records created successfully.")
