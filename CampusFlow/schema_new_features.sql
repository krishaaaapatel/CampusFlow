USE iar_erp;

CREATE TABLE IF NOT EXISTS academic_calendar (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    title       VARCHAR(200) NOT NULL,
    event_date  DATE NOT NULL,
    end_date    DATE,                              
    category    ENUM('holiday','exam','event','deadline','other') DEFAULT 'other',
    description TEXT,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS timetable (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    department  VARCHAR(100) NOT NULL,
    semester    VARCHAR(20)  NOT NULL,
    day_of_week ENUM('Monday','Tuesday','Wednesday','Thursday','Friday','Saturday') NOT NULL,
    start_time  TIME NOT NULL,
    end_time    TIME NOT NULL,
    subject     VARCHAR(100) NOT NULL,
    faculty_name VARCHAR(100),
    room        VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS fees (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    student_id  INT NOT NULL,
    semester    VARCHAR(20) NOT NULL,
    total_fees  DECIMAL(10,2) NOT NULL,
    paid_amount DECIMAL(10,2) NOT NULL DEFAULT 0,
    due_date    DATE,
    FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS exam_schedule (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    department  VARCHAR(100) NOT NULL,
    semester    VARCHAR(20)  NOT NULL,
    subject     VARCHAR(100) NOT NULL,
    exam_date   DATE NOT NULL,
    start_time  TIME NOT NULL,
    end_time    TIME NOT NULL,
    room        VARCHAR(50),
    exam_type   ENUM('mid','end','practical','viva') DEFAULT 'end'
);

CREATE TABLE IF NOT EXISTS results (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    student_id  INT NOT NULL,
    semester    VARCHAR(20)  NOT NULL,
    subject     VARCHAR(100) NOT NULL,
    marks       INT NOT NULL,
    total_marks INT NOT NULL DEFAULT 100,
    grade       VARCHAR(5)   NOT NULL,
    FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS events (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    title        VARCHAR(200) NOT NULL,
    description  TEXT,
    event_date   DATE NOT NULL,
    venue        VARCHAR(150),
    max_seats    INT DEFAULT 100,
    created_at   DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS event_registrations (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    event_id     INT NOT NULL,
    student_id   INT NOT NULL,
    registered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_registration (event_id, student_id),  -- prevent duplicate registration
    FOREIGN KEY (event_id)   REFERENCES events(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES users(id)  ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS circulars (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    title       VARCHAR(200) NOT NULL,
    content     TEXT,
    pdf_link    VARCHAR(300),             -- optional URL to a PDF document
    posted_by   INT NOT NULL,
    posted_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (posted_by) REFERENCES users(id) ON DELETE CASCADE
);

INSERT INTO academic_calendar (title, event_date, end_date, category, description) VALUES
('Republic Day Holiday',     '2026-01-26', NULL,         'holiday',  'National Holiday'),
('Mid Semester Exams Begin', '2026-02-15', '2026-02-22', 'exam',     'Mid semester exams for all departments'),
('Holi Holiday',             '2026-03-14', NULL,         'holiday',  'National Holiday'),
('Tech Fest - Innovate 2026','2026-03-20', '2026-03-21', 'event',    'Annual technical festival'),
('End Semester Exams Begin', '2026-04-20', '2026-05-05', 'exam',     'Final exams for Sem 2'),
('Last Date for Fee Payment','2026-01-15', NULL,         'deadline', 'Pay Sem 2 fees before this date'),
('Summer Vacation Begins',   '2026-05-10', '2026-06-14', 'holiday',  'Summer break');

-- Timetable for BTech SCT Sem 1
INSERT INTO timetable (department, semester, day_of_week, start_time, end_time, subject, faculty_name, room) VALUES
('Btech SCT', 'Sem 1', 'Monday',    '09:00', '10:00', 'Mathematics',      'Dr. Maitri Patel',    'A2-201'),
('Btech SCT', 'Sem 1', 'Monday',    '10:00', '11:00', 'Physics',          'Dr. Sanjay Sonar',    'A2-201'),
('Btech SCT', 'Sem 1', 'Monday',    '11:15', '12:15', 'Programming in C', 'Ms. Devangi K. Parekh','Lab 1'),
('Btech SCT', 'Sem 1', 'Tuesday',   '09:00', '10:00', 'Mathematics',      'Dr. Maitri Patel',    'A2-201'),
('Btech SCT', 'Sem 1', 'Tuesday',   '10:00', '11:00', 'Digital Electronics','Dr. Sanjay Sonar',  'A2-201'),
('Btech SCT', 'Sem 1', 'Wednesday', '09:00', '10:00', 'Programming in C', 'Ms. Devangi K. Parekh','Lab 1'),
('Btech SCT', 'Sem 1', 'Wednesday', '10:00', '11:00', 'Physics',          'Dr. Sanjay Sonar',    'A2-202'),
('Btech SCT', 'Sem 1', 'Thursday',  '09:00', '10:00', 'Mathematics',      'Dr. Maitri Patel',    'A2-201'),
('Btech SCT', 'Sem 1', 'Thursday',  '11:15', '12:15', 'Digital Electronics','Dr. Sanjay Sonar',  'Lab 2'),
('Btech SCT', 'Sem 1', 'Friday',    '09:00', '10:00', 'Programming in C', 'Ms. Devangi K. Parekh','Lab 1'),
('Btech SCT', 'Sem 1', 'Friday',    '10:00', '11:00', 'Mathematics',      'Dr. Maitri Patel',    'A2-201'),
-- Sem 2
('Btech SCT', 'Sem 2', 'Monday',    '09:00', '10:00', 'Data Structures',  'Ms. Devangi K. Parekh','A1-104'),
('Btech SCT', 'Sem 2', 'Monday',    '10:00', '11:00', 'Digital Electronics','Dr. Sanjay Sonar',  'A2-201'),
('Btech SCT', 'Sem 2', 'Tuesday',   '09:00', '10:00', 'Data Structures',  'Ms. Devangi K. Parekh','A1-104'),
('Btech SCT', 'Sem 2', 'Wednesday', '09:00', '10:00', 'Digital Electronics','Dr. Sanjay Sonar',  'A2-201'),
('Btech SCT', 'Sem 2', 'Thursday',  '09:00', '10:00', 'Data Structures',  'Ms. Devangi K. Parekh','Lab 2'),
('Btech SCT', 'Sem 2', 'Friday',    '09:00', '10:00', 'Digital Electronics','Dr. Sanjay Sonar',  'A2-201');

-- Exam Schedule
INSERT INTO exam_schedule (department, semester, subject, exam_date, start_time, end_time, room, exam_type) VALUES
('Btech SCT', 'Sem 2', 'Data Structures',     '2026-04-20', '10:00', '13:00', 'Hall A', 'end'),
('Btech SCT', 'Sem 2', 'Digital Electronics', '2026-04-22', '10:00', '13:00', 'Hall B', 'end'),
('Btech SCT', 'Sem 2', 'Mathematics',         '2026-04-24', '10:00', '13:00', 'Hall A', 'end'),
('Btech SCT', 'Sem 2', 'Programming in C',    '2026-04-26', '10:00', '13:00', 'Lab 1',  'practical'),
('Btech SCT', 'Sem 1', 'Mathematics',         '2026-02-15', '10:00', '12:00', 'Hall A', 'mid'),
('Btech SCT', 'Sem 1', 'Physics',             '2026-02-17', '10:00', '12:00', 'Hall B', 'mid');

-- Results for all 5 students
-- Arjun Verma (id=4)
INSERT INTO results (student_id, semester, subject, marks, total_marks, grade) VALUES
(4,'Sem 1','Mathematics',78,100,'B+'), (4,'Sem 1','Physics',85,100,'A'),
(4,'Sem 1','Programming in C',90,100,'A+'), (4,'Sem 2','Data Structures',72,100,'B'),
(4,'Sem 2','Digital Electronics',80,100,'A');
-- Krisha Patel (id=10)
INSERT INTO results (student_id, semester, subject, marks, total_marks, grade) VALUES
(10,'Sem 1','Mathematics',91,100,'A+'), (10,'Sem 1','Physics',88,100,'A'),
(10,'Sem 1','Programming in C',95,100,'A+'), (10,'Sem 2','Data Structures',89,100,'A'),
(10,'Sem 2','Digital Electronics',76,100,'B+');
-- Laksh Trivedi (id=11)
INSERT INTO results (student_id, semester, subject, marks, total_marks, grade) VALUES
(11,'Sem 1','Mathematics',65,100,'B'), (11,'Sem 1','Physics',70,100,'B+'),
(11,'Sem 1','Programming in C',60,100,'B'), (11,'Sem 2','Data Structures',55,100,'C'),
(11,'Sem 2','Digital Electronics',68,100,'B');
-- Veer Parsaniya (id=12)
INSERT INTO results (student_id, semester, subject, marks, total_marks, grade) VALUES
(12,'Sem 1','Mathematics',82,100,'A'), (12,'Sem 1','Physics',74,100,'B+'),
(12,'Sem 1','Programming in C',88,100,'A'), (12,'Sem 2','Data Structures',79,100,'B+'),
(12,'Sem 2','Digital Electronics',85,100,'A');
-- Neer Marvaniya (id=13)
INSERT INTO results (student_id, semester, subject, marks, total_marks, grade) VALUES
(13,'Sem 1','Mathematics',58,100,'C'), (13,'Sem 1','Physics',62,100,'B'),
(13,'Sem 1','Programming in C',71,100,'B+'), (13,'Sem 2','Data Structures',66,100,'B'),
(13,'Sem 2','Digital Electronics',59,100,'C');

-- Fees for all 5 students
INSERT INTO fees (student_id, semester, total_fees, paid_amount, due_date) VALUES
(4,  'Sem 1', 45000, 45000, '2025-08-01'), (4,  'Sem 2', 45000, 20000, '2026-01-15'),
(10, 'Sem 1', 45000, 45000, '2025-08-01'), (10, 'Sem 2', 45000, 45000, '2026-01-15'),
(11, 'Sem 1', 45000, 30000, '2025-08-01'), (11, 'Sem 2', 45000, 0,     '2026-01-15'),
(12, 'Sem 1', 45000, 45000, '2025-08-01'), (12, 'Sem 2', 45000, 15000, '2026-01-15'),
(13, 'Sem 1', 45000, 45000, '2025-08-01'), (13, 'Sem 2', 45000, 0,     '2026-01-15');

-- Events
INSERT INTO events (title, description, event_date, venue, max_seats) VALUES
('Tech Fest - Innovate 2026', 'Annual technical festival with coding competitions, robotics, and more!', '2026-03-20', 'Main Auditorium', 200),
('Cultural Night 2026',       'An evening of music, dance and drama by IAR students.',                  '2026-03-15', 'Open Air Theatre',  300),
('Career Fair 2026',          'Meet top recruiters from IT and engineering companies.',                  '2026-02-28', 'Conference Hall',   150),
('Workshop: Python & AI',     'Hands-on workshop on Python programming and AI basics.',                 '2026-02-10', 'Lab 3',              40);

-- Circulars
INSERT INTO circulars (title, content, pdf_link, posted_by) VALUES
('Exam Timetable Released',       'The end semester exam timetable for Sem 2 has been released. Please check the Exam Schedule section.', NULL, 4),
('Fee Payment Reminder',          'Last date for Sem 2 fee payment is 15th January 2026. Students with pending fees please pay immediately.', NULL, 4),
('Anti-Ragging Policy 2026',      'All students must read the updated anti-ragging policy. Zero tolerance will be maintained.', 'https://www.ugc.gov.in/antiRagging', 4),
('Scholarship Applications Open', 'Applications for merit scholarships are now open. Last date: 31st January 2026. Apply via the admin office.', NULL, 4);
