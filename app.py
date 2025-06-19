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
    return render_template("index.html")

# API 端點：取得所有認證
@app.route('/api/certifications')
def api_certifications():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT ID, Title, Description, URL FROM Certifications ORDER BY Title")
        certs = cursor.fetchall()
        conn.close()
        
        # 轉換為字典格式
        result = []
        for cert in certs:
            result.append({
                'id': cert[0],
                'title': cert[1],
                'description': cert[2],
                'url': cert[3]
            })
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API 端點：取得特定認證的課程
@app.route('/api/courses/<int:cert_id>')
def api_courses(cert_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT ID, Title, Description, URL FROM Courses WHERE CertificationID=? ORDER BY Title", cert_id)
        courses = cursor.fetchall()
        conn.close()
        
        # 轉換為字典格式
        result = []
        for course in courses:
            result.append({
                'id': course[0],
                'title': course[1],
                'description': course[2],
                'url': course[3]
            })
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API 端點：取得特定課程的模組
@app.route('/api/modules/<int:course_id>')
def api_modules(course_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT ID, Title, Description, URL FROM Modules WHERE CourseID=? ORDER BY Title", course_id)
        modules = cursor.fetchall()
        conn.close()
        
        # 轉換為字典格式
        result = []
        for module in modules:
            result.append({
                'id': module[0],
                'title': module[1],
                'description': module[2],
                'url': module[3]
            })
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 舊的路由（保留向後相容性）
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