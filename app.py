from flask import Flask, render_template, jsonify
import pyodbc

app = Flask(__name__)

# 資料庫連線設定
def get_connection():
    return pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=DESKTOP-5IK5K0N\\MSSQL2022;'
        'DATABASE=microsoft;'
        'Trusted_Connection=yes;'
    )

@app.route('/')
def index():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT ID, Title, Description FROM Certifications")
    certs = cursor.fetchall()
    conn.close()
    
    # 用 render_template 顯示 (或改成 jsonify 回傳 JSON)
    return render_template("index.html", certs=certs)

@app.route('/cert/<int:cert_id>')
def cert_detail(cert_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT Title, Description FROM Certifications WHERE ID=?", cert_id)
    cert = cursor.fetchone()

    cursor.execute("SELECT ID, Title FROM Courses WHERE CertificationID=?", cert_id)
    courses = cursor.fetchall()
    conn.close()

    return render_template("cert_detail.html", cert=cert, courses=courses)

@app.route('/course/<int:course_id>')
def course_detail(course_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT Title, Description FROM Courses WHERE ID=?", course_id)
    course = cursor.fetchone()

    cursor.execute("SELECT Title, Description FROM Modules WHERE CourseID=?", course_id)
    modules = cursor.fetchall()
    conn.close()

    return render_template("course_detail.html", course=course, modules=modules)

if __name__ == "__main__":
    app.run(debug=True)
