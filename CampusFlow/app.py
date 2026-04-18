from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
import os
from datetime import date

app = Flask(__name__)
app.secret_key = "iar_university_secret_key_2025"

UPLOAD_FOLDER = os.path.join("static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

def get_db():
    return mysql.connector.connect(
        host     = "localhost",
        user     = "root",
        password = "your_password",   # <-- YOUR MYSQL PASSWORD
        database = "iar_erp"
    )

def is_logged_in():
    return "user_id" in session

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def index():
    db = get_db(); cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT notices.title, notices.content, notices.posted_at, users.name AS author
        FROM notices JOIN users ON notices.posted_by = users.id
        ORDER BY notices.posted_at DESC LIMIT 3
    """)
    notices = cursor.fetchall()
    cursor.close(); db.close()
    return render_template("index.html", notices=notices)

@app.route("/login", methods=["GET", "POST"])
def login():
    if is_logged_in():
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        email    = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        db = get_db(); cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email=%s AND password=%s", (email, password))
        user = cursor.fetchone()
        cursor.close(); db.close()
        if user:
            session["user_id"]   = user["id"]
            session["user_name"] = user["name"]
            session["user_role"] = user["role"]
            session["user_dept"] = user.get("department", "")
            flash(f"Welcome back, {user['name']}!", "success")
            return redirect(url_for("dashboard"))
        flash("Incorrect email or password.", "danger")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))

@app.route("/dashboard")
def dashboard():
    if not is_logged_in():
        flash("Please log in first.", "warning")
        return redirect(url_for("login"))
    db = get_db(); cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id=%s", (session["user_id"],))
    user = cursor.fetchone()
    cursor.execute("""
        SELECT notices.title, notices.content, notices.posted_at, users.name AS author
        FROM notices JOIN users ON notices.posted_by = users.id
        ORDER BY notices.posted_at DESC
    """)
    notices = cursor.fetchall()
    conversations = []
    if session["user_role"] == "faculty":
        cursor.execute("""
            SELECT conversations.id, conversations.status, conversations.started_at,
                   COUNT(chat_messages.id) AS message_count
            FROM conversations
            LEFT JOIN chat_messages ON chat_messages.conversation_id = conversations.id
            WHERE conversations.faculty_id = %s
            GROUP BY conversations.id ORDER BY conversations.started_at DESC
        """, (session["user_id"],))
        conversations = cursor.fetchall()
    elif session["user_role"] == "student":
        cursor.execute("""
            SELECT conversations.id, conversations.status, conversations.started_at,
                   users.name AS faculty_name,
                   COUNT(chat_messages.id) AS message_count
            FROM conversations
            JOIN users ON conversations.faculty_id = users.id
            LEFT JOIN chat_messages ON chat_messages.conversation_id = conversations.id
            WHERE conversations.student_id = %s
            GROUP BY conversations.id ORDER BY conversations.started_at DESC
        """, (session["user_id"],))
        conversations = cursor.fetchall()
    cursor.close(); db.close()
    return render_template("dashboard.html", user=user, notices=notices, conversations=conversations)

@app.route("/profile/edit", methods=["GET", "POST"])
def edit_profile():
    if not is_logged_in():
        return redirect(url_for("login"))
    db = get_db(); cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id=%s", (session["user_id"],))
    user = cursor.fetchone()
    if request.method == "POST":
        cursor.execute("""
            UPDATE users SET phone=%s, address=%s, dob=%s, blood_group=%s,
            parent_name=%s, parent_phone=%s, enrollment_no=%s WHERE id=%s
        """, (
            request.form.get("phone","").strip(),
            request.form.get("address","").strip(),
            request.form.get("dob","") or None,
            request.form.get("blood_group","").strip(),
            request.form.get("parent_name","").strip(),
            request.form.get("parent_phone","").strip(),
            request.form.get("enrollment_no","").strip(),
            session["user_id"]
        ))
        db.commit()
        flash("Profile updated!", "success")
        return redirect(url_for("dashboard"))
    cursor.close(); db.close()
    return render_template("edit_profile.html", user=user)

@app.route("/chat", methods=["GET", "POST"])
def chat():
    if not is_logged_in():
        flash("Please log in first.", "warning")
        return redirect(url_for("login"))
    db = get_db(); cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, name, department FROM users WHERE role='faculty' ORDER BY name")
    faculty_list = cursor.fetchall()
    if request.method == "POST":
        faculty_id    = request.form.get("faculty_id")
        first_message = request.form.get("message", "").strip()
        if not faculty_id or not first_message:
            flash("Please select a faculty and type a message.", "warning")
        else:
            cursor.execute("INSERT INTO conversations (student_id, faculty_id) VALUES (%s,%s)",
                           (session["user_id"], faculty_id))
            db.commit()
            conv_id = cursor.lastrowid
            cursor.execute("INSERT INTO chat_messages (conversation_id, sender_role, message) VALUES (%s,'student',%s)",
                           (conv_id, first_message))
            db.commit()
            flash("Conversation started anonymously!", "success")
            return redirect(url_for("conversation", conv_id=conv_id))
    cursor.close(); db.close()
    return render_template("chat.html", faculty_list=faculty_list)


@app.route("/conversation/<int:conv_id>", methods=["GET", "POST"])
def conversation(conv_id):
    if not is_logged_in():
        return redirect(url_for("login"))
    db = get_db(); cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM conversations WHERE id=%s", (conv_id,))
    conv = cursor.fetchone()
    if not conv:
        flash("Conversation not found.", "danger")
        return redirect(url_for("dashboard"))
    if session["user_role"] == "student" and conv["student_id"] != session["user_id"]:
        flash("Access denied.", "danger"); return redirect(url_for("dashboard"))
    if session["user_role"] == "faculty" and conv["faculty_id"] != session["user_id"]:
        flash("Access denied.", "danger"); return redirect(url_for("dashboard"))
    if request.method == "POST" and conv["status"] == "active":
        message = request.form.get("message", "").strip()
        if message:
            cursor.execute("INSERT INTO chat_messages (conversation_id, sender_role, message) VALUES (%s,%s,%s)",
                           (conv_id, session["user_role"], message))
            db.commit()
    cursor.execute("SELECT * FROM chat_messages WHERE conversation_id=%s ORDER BY sent_at ASC", (conv_id,))
    messages = cursor.fetchall()
    cursor.execute("SELECT name FROM users WHERE id=%s", (conv["faculty_id"],))
    faculty = cursor.fetchone()
    cursor.close(); db.close()
    return render_template("conversation.html", conv=conv, messages=messages, faculty=faculty)


@app.route("/end-conversation/<int:conv_id>")
def end_conversation(conv_id):
    if not is_logged_in() or session["user_role"] != "student":
        flash("Only students can end a conversation.", "danger")
        return redirect(url_for("dashboard"))
    db = get_db(); cursor = db.cursor()
    cursor.execute("UPDATE conversations SET status='ended' WHERE id=%s AND student_id=%s",
                   (conv_id, session["user_id"]))
    db.commit(); cursor.close(); db.close()
    flash("Conversation ended.", "info")
    return redirect(url_for("dashboard"))

@app.route("/lost-found", methods=["GET", "POST"])
def lost_found():
    db = get_db(); cursor = db.cursor(dictionary=True)
    if request.method == "POST":
        item_type   = request.form.get("type")
        item_name   = request.form.get("item_name", "").strip()
        description = request.form.get("description", "").strip()
        contact     = request.form.get("contact", "").strip()
        image_filename = None
        if "image" in request.files:
            file = request.files["image"]
            if file and file.filename != "" and allowed_file(file.filename):
                ext = file.filename.rsplit(".", 1)[1].lower()
                image_filename = f"{item_name.replace(' ','_')}_{os.urandom(4).hex()}.{ext}"
                file.save(os.path.join(app.config["UPLOAD_FOLDER"], image_filename))
        if not item_name or not contact:
            flash("Item name and contact are required.", "warning")
        else:
            cursor.execute("INSERT INTO lost_and_found (type,item_name,description,contact,image) VALUES (%s,%s,%s,%s,%s)",
                           (item_type, item_name, description, contact, image_filename))
            db.commit()
            flash("Post added to Lost & Found!", "success")
    cursor.execute("SELECT * FROM lost_and_found ORDER BY posted_at DESC")
    items = cursor.fetchall()
    cursor.close(); db.close()
    return render_template("lost_found.html", items=items)

@app.route("/map")
def faculty_map():
    db = get_db(); cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT name, department, room_number FROM users WHERE role='faculty' ORDER BY department")
    faculty = cursor.fetchall()
    cursor.close(); db.close()
    return render_template("map.html", faculty=faculty)

@app.route("/academic-calendar")
def academic_calendar():
    if not is_logged_in():
        flash("Please log in first.", "warning")
        return redirect(url_for("login"))
    db = get_db(); cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM academic_calendar ORDER BY event_date ASC")
    events = cursor.fetchall()
    cursor.close(); db.close()
    grouped = {}
    for e in events:
        cat = e["category"]
        if cat not in grouped:
            grouped[cat] = []
        grouped[cat].append(e)
    return render_template("academic_calendar.html", events=events, grouped=grouped)

@app.route("/timetable")
def timetable():
    if not is_logged_in():
        flash("Please log in first.", "warning")
        return redirect(url_for("login"))
    db = get_db(); cursor = db.cursor(dictionary=True)
    dept     = session.get("user_dept", "")
    semester = request.args.get("semester", "Sem 1")
    cursor.execute("SELECT DISTINCT semester FROM timetable WHERE department=%s ORDER BY semester", (dept,))
    semesters = [r["semester"] for r in cursor.fetchall()]
    cursor.execute("""
        SELECT * FROM timetable
        WHERE department=%s AND semester=%s
        ORDER BY FIELD(day_of_week,'Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'), start_time
    """, (dept, semester))
    rows = cursor.fetchall()
    days_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]
    timetable_data = {day: [] for day in days_order}
    for row in rows:
        timetable_data[row["day_of_week"]].append(row)
    cursor.close(); db.close()
    return render_template("timetable.html", timetable_data=timetable_data,
                           days_order=days_order, semesters=semesters,
                           selected_sem=semester, dept=dept)
    
@app.route("/fees")
def fees():
    if not is_logged_in() or session["user_role"] != "student":
        flash("Only students can view fees.", "warning")
        return redirect(url_for("dashboard"))
    db = get_db(); cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT semester, total_fees, paid_amount,
               (total_fees - paid_amount) AS remaining, due_date
        FROM fees WHERE student_id=%s ORDER BY semester
    """, (session["user_id"],))
    fee_records = cursor.fetchall()
    cursor.close(); db.close()
    total     = sum(f["total_fees"]  for f in fee_records)
    paid      = sum(f["paid_amount"] for f in fee_records)
    remaining = sum(f["remaining"]   for f in fee_records)
    return render_template("fees.html", fee_records=fee_records,
                           total=total, paid=paid, remaining=remaining)

@app.route("/exam-schedule")
def exam_schedule():
    if not is_logged_in():
        flash("Please log in first.", "warning")
        return redirect(url_for("login"))
    db = get_db(); cursor = db.cursor(dictionary=True)
    dept = session.get("user_dept", "")
    if session["user_role"] == "student":
        cursor.execute("""
            SELECT * FROM exam_schedule
            WHERE department=%s ORDER BY exam_date ASC
        """, (dept,))
    else:
        cursor.execute("SELECT * FROM exam_schedule ORDER BY exam_date ASC")
    exams = cursor.fetchall()
    cursor.close(); db.close()
    return render_template("exam_schedule.html", exams=exams)

@app.route("/results")
def results():
    if not is_logged_in() or session["user_role"] != "student":
        flash("Only students can view results.", "warning")
        return redirect(url_for("dashboard"))
    db = get_db(); cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT semester, subject, marks, total_marks, grade
        FROM results WHERE student_id=%s ORDER BY semester, subject
    """, (session["user_id"],))
    all_results = cursor.fetchall()
    cursor.close(); db.close()
    semesters = {}
    for row in all_results:
        sem = row["semester"]
        if sem not in semesters:
            semesters[sem] = []
        semesters[sem].append(row)
    return render_template("results.html", semesters=semesters)

@app.route("/events")
def events():
    if not is_logged_in():
        flash("Please log in first.", "warning")
        return redirect(url_for("login"))
    db = get_db(); cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT events.*,
               COUNT(event_registrations.id) AS registered_count
        FROM events
        LEFT JOIN event_registrations ON events.id = event_registrations.event_id
        GROUP BY events.id
        ORDER BY events.event_date ASC
    """)
    all_events = cursor.fetchall()
    my_registrations = set()
    if session["user_role"] == "student":
        cursor.execute("SELECT event_id FROM event_registrations WHERE student_id=%s",
                       (session["user_id"],))
        my_registrations = {r["event_id"] for r in cursor.fetchall()}
    cursor.close(); db.close()
    return render_template("events.html", all_events=all_events,
                           my_registrations=my_registrations)


@app.route("/events/register/<int:event_id>")
def register_event(event_id):
    if not is_logged_in() or session["user_role"] != "student":
        flash("Only students can register for events.", "warning")
        return redirect(url_for("events"))
    db = get_db(); cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT events.max_seats, COUNT(event_registrations.id) AS registered_count
        FROM events
        LEFT JOIN event_registrations ON events.id = event_registrations.event_id
        WHERE events.id=%s GROUP BY events.id
    """, (event_id,))
    ev = cursor.fetchone()
    if ev and ev["registered_count"] < ev["max_seats"]:
        try:
            cursor.execute("INSERT INTO event_registrations (event_id, student_id) VALUES (%s,%s)",
                           (event_id, session["user_id"]))
            db.commit()
            flash("Successfully registered for the event!", "success")
        except:
            flash("You are already registered for this event.", "warning")
    else:
        flash("Sorry, this event is full.", "danger")
    cursor.close(); db.close()
    return redirect(url_for("events"))


@app.route("/events/unregister/<int:event_id>")
def unregister_event(event_id):
    if not is_logged_in() or session["user_role"] != "student":
        return redirect(url_for("events"))
    db = get_db(); cursor = db.cursor()
    cursor.execute("DELETE FROM event_registrations WHERE event_id=%s AND student_id=%s",
                   (event_id, session["user_id"]))
    db.commit(); cursor.close(); db.close()
    flash("Registration cancelled.", "info")
    return redirect(url_for("events"))

@app.route("/circulars")
def circulars():
    if not is_logged_in():
        flash("Please log in first.", "warning")
        return redirect(url_for("login"))
    db = get_db(); cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT circulars.*, users.name AS posted_by_name
        FROM circulars
        JOIN users ON circulars.posted_by = users.id
        ORDER BY circulars.posted_at DESC
    """)
    all_circulars = cursor.fetchall()
    cursor.close(); db.close()
    return render_template("circulars.html", circulars=all_circulars)


@app.route("/circulars/add", methods=["GET", "POST"])
def add_circular():
    if not is_logged_in() or session["user_role"] != "faculty":
        flash("Only faculty can post circulars.", "danger")
        return redirect(url_for("circulars"))
    if request.method == "POST":
        title    = request.form.get("title","").strip()
        content  = request.form.get("content","").strip()
        pdf_link = request.form.get("pdf_link","").strip()
        if title:
            db = get_db(); cursor = db.cursor()
            cursor.execute("INSERT INTO circulars (title, content, pdf_link, posted_by) VALUES (%s,%s,%s,%s)",
                           (title, content, pdf_link or None, session["user_id"]))
            db.commit(); cursor.close(); db.close()
            flash("Circular posted!", "success")
            return redirect(url_for("circulars"))
        flash("Title is required.", "warning")
    return render_template("add_circular.html")

@app.route("/attendance/mark", methods=["GET", "POST"])
def mark_attendance():
    if not is_logged_in() or session["user_role"] != "faculty":
        flash("Only faculty can mark attendance.", "danger")
        return redirect(url_for("dashboard"))

    db = get_db(); cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT id, name FROM users WHERE role='student' ORDER BY name")
    students = cursor.fetchall()

    if request.method == "POST":
        subject = request.form.get("subject", "").strip()
        att_date = request.form.get("date", "").strip()

        if not subject or not att_date:
            flash("Please enter both subject and date.", "warning")
        else:
            cursor.execute(
                "DELETE FROM attendance WHERE faculty_id=%s AND subject=%s AND date=%s",
                (session["user_id"], subject, att_date)
            )
            for student in students:
                status = request.form.get(f"status_{student['id']}", "absent")
                cursor.execute(
                    "INSERT INTO attendance (student_id, faculty_id, subject, date, status) VALUES (%s,%s,%s,%s,%s)",
                    (student["id"], session["user_id"], subject, att_date, status)
                )
            db.commit()
            flash(f"Attendance saved for {subject} on {att_date}!", "success")
    cursor.execute("""
        SELECT subject, date,
               SUM(status='present') AS present_count,
               SUM(status='absent')  AS absent_count
        FROM attendance
        WHERE faculty_id=%s
        GROUP BY subject, date
        ORDER BY date DESC, subject
        LIMIT 20
    """, (session["user_id"],))
    history = cursor.fetchall()

    cursor.close(); db.close()
    return render_template("mark_attendance.html", students=students,
                           history=history, today=date.today())

@app.route("/attendance")
def view_attendance():
    if not is_logged_in() or session["user_role"] != "student":
        flash("Only students can view attendance.", "warning")
        return redirect(url_for("dashboard"))

    db = get_db(); cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT subject,
               COUNT(*)                                          AS total_classes,
               SUM(status='present')                            AS present,
               SUM(status='absent')                             AS absent,
               ROUND(SUM(status='present') * 100.0 / COUNT(*), 1) AS percentage
        FROM attendance
        WHERE student_id=%s
        GROUP BY subject
        ORDER BY subject
    """, (session["user_id"],))
    summary = cursor.fetchall()

    cursor.execute("""
        SELECT subject, date, status
        FROM attendance
        WHERE student_id=%s
        ORDER BY date DESC, subject
    """, (session["user_id"],))
    details = cursor.fetchall()

    cursor.close(); db.close()
    return render_template("attendance.html", summary=summary, details=details)

if __name__ == "__main__":
    app.run(debug=True)
