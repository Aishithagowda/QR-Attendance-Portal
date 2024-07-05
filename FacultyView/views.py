from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Student
import qrcode
import socket
from StudentView.views import present,scanned_devices
from io import BytesIO
from django.http import HttpResponse
import pandas as pd
from django.views.decorators.cache import never_cache

def qrgenerator(date, times, subject):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]

    

    link = f"http://{ip}:8000/add_manually?date={date}&time={times}&subject={subject}"

    # Function to generate and display a QR code
    def generate_qr_code(link):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(link)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        imagepath = f"FacultyView/static/FacultyView/qrcode.png"
        img.save(imagepath)
        

    generate_qr_code(link)

def export_to_excel(students, attendance_context):
    data = []
    date = attendance_context.get('date', '')
    time = attendance_context.get('time', '')
    subject = attendance_context.get('subject', '')
    for student in students:
        data.append([student.s_roll, student.s_fname, student.s_lname, student.s_branch.branch, student.s_year.year, student.s_section.section])
    
    df = pd.DataFrame(data, columns=['USN', 'First Name', 'Last Name', 'Branch', 'Year', 'Section'])
    filename = f"attendance_{date}_{time}_{subject}.xlsx"
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Attendance')
    
    buffer.seek(0)
    return filename, buffer

@never_cache
def faculty_view(request):
   if request.method == "POST":
        print(request)
        if 'student_id' in request.POST:
            print('Hi')
            student_roll = request.POST["student_id"]
            student = Student.objects.get(s_roll=student_roll)
            if student in present:
                present.remove(student)
        elif 'date' in request.POST and 'time' in request.POST and 'subject' in request.POST:
            print('Hello')
            date = request.POST["date"]
            time = request.POST["time"]
            subject = request.POST["subject"]
            request.session['attendance_context'] = {
                'date': date,
                'time': time,
                'subject': subject,
            }
            qrfilename = qrgenerator(date, time, subject)
        elif 'submit' in request.POST:
            print('yo')
            attendance_context = request.session.get('attendance_context', {})
            filename, excel_file = export_to_excel(present, attendance_context)
            response = HttpResponse(excel_file, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            present.clear()
            scanned_devices.clear()
            
            return response
        return HttpResponseRedirect("/")
   else:
        return render(
            request,
            "FacultyView/FacultyViewIndex.html",
            {
                "students": present,
                
            },
        )

    


def add_manually(request):
    students = Student.objects.all().order_by("s_roll")
    attendance_context = request.session.get('attendance_context', {})
    return render(
        request,
        "StudentView/StudentViewIndex.html",
        {
            "students": students,
            "date": request.GET.get('date') or attendance_context.get('date', ''),
            "time": request.GET.get('time') or attendance_context.get('time', ''),
            "subject": request.GET.get('subject') or attendance_context.get('subject', ''),
        },
    )
