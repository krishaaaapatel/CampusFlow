
USE iar_erp;

CREATE TABLE IF NOT EXISTS attendance (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    student_id  INT NOT NULL,
    faculty_id  INT NOT NULL,
    subject     VARCHAR(100) NOT NULL,
    date        DATE NOT NULL,
    status      ENUM('present','absent') NOT NULL,
    FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (faculty_id) REFERENCES users(id) ON DELETE CASCADE
);
