# db_handler.py
import pyodbc

class DBHandler:
    def __init__(self, server, database):
        self.conn = pyodbc.connect(
            f'DRIVER={{ODBC Driver 17 for SQL Server}};'
            f'SERVER={server};DATABASE={database};'
            f'Trusted_Connection=yes;'
        )
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):

        # 刪除舊表（如果存在）
        self.cursor.execute('''
            IF OBJECT_ID('Modules', 'U') IS NOT NULL DROP TABLE Modules;
            IF OBJECT_ID('Courses', 'U') IS NOT NULL DROP TABLE Courses;
            IF OBJECT_ID('Certifications', 'U') IS NOT NULL DROP TABLE Certifications;
        ''')

        ### ertifications ###
        self.cursor.execute('''
            IF OBJECT_ID('Certifications', 'U') IS NULL
            CREATE TABLE Certifications (
                ID INT IDENTITY(1,1) PRIMARY KEY,
                Title NVARCHAR(255),
                URL NVARCHAR(MAX),
                Description NVARCHAR(MAX)
            )
        ''')
        ###### coursrs ######
        self.cursor.execute('''
            IF OBJECT_ID('Courses', 'U') IS NULL
            CREATE TABLE Courses (
                ID INT IDENTITY(1,1) PRIMARY KEY,
                CertificationID INT,
                Title NVARCHAR(255),
                URL NVARCHAR(MAX),
                Description NVARCHAR(MAX),
                FOREIGN KEY (CertificationID) REFERENCES Certifications(ID)
            )
        ''')
        ###### module ######
        self.cursor.execute('''
            IF OBJECT_ID('Modules', 'U') IS NULL
            CREATE TABLE Modules (
                ID INT IDENTITY(1,1) PRIMARY KEY,
                CourseID INT,
                Title NVARCHAR(255),
                URL NVARCHAR(MAX),
                Description NVARCHAR(MAX),
                FOREIGN KEY (CourseID) REFERENCES Courses(ID)
            )
        ''')

    #	取得或建立認證，回傳 ID
    def get_or_create_certification(self, title, url, desc):
        #print(f"查找認證: {title}")
        self.cursor.execute('SELECT ID FROM Certifications WHERE Title = ?', (title,))
        row = self.cursor.fetchone()
        if row:
            #print(f"✅ 找到認證 {title} → ID: {row[0]}")
            return row[0]
        else:
            #print(f"🚧 沒找到認證，插入新認證：{title}")
            self.cursor.execute('INSERT INTO Certifications (Title, URL, Description) OUTPUT INSERTED.ID VALUES (?, ?, ?)', (title, url, desc))
            new_id = self.cursor.fetchone()[0]
            self.conn.commit()
            #print(f"✨ 新增認證完成 → ID: {new_id}")
            return new_id
    
    #   取得或建立課程，回傳 ID
    def get_or_create_course(self, title, url, desc, cert_id):
        self.cursor.execute('SELECT ID FROM Courses WHERE Title = ? AND CertificationID = ?',(title, cert_id))
        row = self.cursor.fetchone()
        if row:
            return row[0]
        else:
            self.cursor.execute('INSERT INTO Courses (Title, CertificationID, URL, Description) OUTPUT INSERTED.ID VALUES (?, ?, ?, ?);',(title, cert_id, url, desc))
            new_id = self.cursor.fetchone()[0]
            return new_id

    
    #   取得或建立模組，回傳 ID
    def insert_module(self, title, url, description, course_id):
        self.cursor.execute('SELECT ID FROM Modules WHERE Title = ? AND CourseID = ?', (title, course_id))
        row = self.cursor.fetchone()
        if row:
            return row[0]  
        else:
            self.cursor.execute('INSERT INTO Modules (Title, CourseID, URL, Description) VALUES (?, ?, ?, ?)', (title, course_id, url, description))
            self.conn.commit()
            return self.cursor.execute('SELECT SCOPE_IDENTITY()').fetchone()[0]
                
    def insert_course_structure(self, certification_title, certification_url, certification_description, course_title, course_url, course_description, modules):
        """
        modules: List of dicts, each with 'title', 'url', 'description'
        """
        cert_id = self.get_or_create_certification(certification_title, certification_url, certification_description)
        course_id = self.get_or_create_course(course_title, course_url, course_description, cert_id)
        #print(f"🎯 get_or_create_course 回傳的 course_id: {course_id}")
        for module in modules:
            #print(f"📌 Course ID: {course_id} - 插入模組: {module['title']}")
            self.insert_module(
                title=module['title'],
                course_id=course_id,
                url=module['url'],
                description=module['description']
            )

    def commit(self):
        self.conn.commit()

    def close(self):
        self.cursor.close()
        self.conn.close()