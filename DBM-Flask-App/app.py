import os
import csv
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy

UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS_CSV = {'csv'}
ALLOWED_EXTENSIONS_IMG = {'jpg','jpeg','png'}

app = Flask(__name__ ,static_url_path="", static_folder="uploads")
app.secret_key = "super secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///details.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Details(db.Model):
    name = db.Column(db.String(200), nullable=False, primary_key=True)
    state = db.Column(db.String(100))
    salary = db.Column(db.Integer)
    grade = db.Column(db.Integer)
    room = db.Column(db.Integer)
    cno = db.Column(db.Integer)
    pic = db.Column(db.String(200))
    keywords = db.Column(db.String(1000))

    def __repr__(self) -> str:
        return f"{self.name}"

def allowed_file_csv(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_CSV
        
def allowed_file_img(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_IMG

@app.route("/")
def home():
    allDetails = Details.query.all()
    return render_template('home.html', allDetails = allDetails)

@app.route("/upload_csv", methods=['GET', 'POST'])
def upload_csv():
    error=None
    success = None
    allDetails = []
    allErrors = []
    if request.method == 'POST':
        file = request.files['csvfile']
        # check if the post request has the file part
        if 'csvfile' not in request.files:
            error = "No file Part present"

        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        elif file.filename == '':
            error = "No File Selected"

        elif allowed_file_csv(file.filename) != True:
            error = "Please upload a csv file"

        if file and allowed_file_csv(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            success = "File Uploaded Successfully!"
            path = "./uploads/"+file.filename
            all_details = pd.read_csv(path, encoding="ISO-8859-1")
            for index, row in all_details.iterrows():
                name = row['Name']
                state = row['State']
                salary = row['Salary']
                if isinstance(salary, str):
                    salary = salary.strip()
                if pd.isna(salary) or salary == None or salary == '':
                    salary =-1
                grade = row['Grade']
                room = row['Room']
                cno = row['Telnum']
                pic = row['Picture']
                if isinstance(pic, str):
                    pic = pic.strip()
                if pd.isna(pic) or pic == None or pic == '':
                    pic ="No Name Submitted"
                keywords = row['Keywords']
                details = Details(name = name, state = state, salary= salary, grade = grade, room = room, cno = cno, pic = pic, keywords = keywords)
                query_details = Details.query.filter_by(name=name).first()
                query_pic = Details.query.filter_by(pic = pic).first()
                if query_details == None and (query_pic == None or query_pic.pic == 'No Name Submitted'):
                    db.session.add(details)
                    db.session.commit() 
                else:
                    #print("Error in entry!  ", name, "  ", query_pic.pic)
                    success = None
                    error = "Entries with the following name(s) not uploaded as ones with the same name or image name already exist in the database:"
                    allErrors.append(name)
    
    allDetails = Details.query.all()
    return render_template('home.html', error = error, success = success, allDetails = allDetails, allErrors= allErrors)

@app.route("/upload_img", methods=['GET', 'POST'])
def upload_img():
    img_error=None
    img_success = None
    if request.method == 'POST':
        file = request.files['imgfile']
        # check if the post request has the file part
        if 'imgfile' not in request.files:
            img_error = "No file Part present"

        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        elif file.filename == '':
            img_error = "No File Selected"

        elif allowed_file_img(file.filename) != True:
            img_error = "Please upload an image file"

        if file and allowed_file_img(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            img_success = "File Uploaded Successfully!"
            path = "./uploads/"+file.filename
    allDetails = Details.query.all()
    return render_template('home.html', img_error = img_error, img_success = img_success, allDetails = allDetails)


@app.route("/delete/<string:name>")
def delete(name):
    details = Details.query.filter_by(name = name).first()
    db.session.delete(details)
    db.session.commit()
    #delete the image file as well
    if allowed_file_img(details.pic) and os.path.exists("./uploads/"+details.pic):
        os.remove("./uploads/"+details.pic)
    return redirect("/")

@app.route("/update/<string:name>", methods=['GET', 'POST'])
def update(name):
    details = Details.query.filter_by(name = name).first()
    if request.method=='POST':
        error = None
        state = request.form['state']
        salary = request.form['salary']
        if isinstance(salary, str):
             salary = salary.strip()
        if pd.isna(salary) or salary == None or salary == '':
            salary =-1
        grade = request.form['grade']
        room = request.form['room']
        cno = request.form['cno']
        pic = request.form['pic']
        keywords = request.form['keywords']
        query_pic = Details.query.filter_by(pic = pic).first()

        if query_pic!= None and query_pic.pic!=details.pic:
            error = "A pic with the same name already exists in the DB"
            return render_template('update.html', details = details, error=error)

        if allowed_file_img(pic) == False:
            print("Name wrong")
            error = "Picture name can only end with .jpg, .png or .jpeg"
            return render_template('update.html', details = details, error=error)

        details = Details.query.filter_by(name=name).first()
        details.state = state
        details.salary = salary
        details.grade = grade
        details.room = room
        details.cno = cno
        
        details.pic = pic
        details.keywords = keywords

        db.session.add(details)
        db.session.commit()
        return redirect("/")

    return render_template('update.html', details = details)

@app.route("/searchname" , methods=['GET', 'POST'])
def search_name():
    if request.method == 'POST':
        name = request.form['name']
        print(name)
        details = Details.query.filter_by(name = name).first()
        print(details )
        return render_template('searchname.html', details = details)
    return redirect("/")

@app.route("/filtersalary" , methods=['GET', 'POST'])
def filter_salary():
    if request.method =='POST':
        salary = request.form['salary']
        if len(salary) == 0:
            return redirect("/")        
        if request.form['action'] == 'greaterthan':
            
            print(salary)
            allDetails = Details.query.filter(Details.salary > salary)
            return render_template('searchsalary.html', allDetails = allDetails)
        else:
            print(salary)
            allDetails = Details.query.filter(Details.salary < salary)
            print(allDetails.count())
            return render_template('searchsalary.html', allDetails = allDetails)
    return redirect("/")

@app.route("/addnew" , methods=['GET', 'POST'])
def addnew():
    return render_template('newentry.html')

@app.route("/addnewentry" , methods=['GET', 'POST'])
def addnewentry():
    error = None
    if request.method == 'POST':
        name = request.form['name']
        state = request.form['state']
        salary = request.form['salary']
        grade = request.form['grade']
        room = request.form['room']
        cno = request.form['cno']
        pic = request.form['pic']

        if isinstance(pic, str):
            pic = pic.strip()
            if allowed_file_img(pic) == False:
                error = "Image extension is wrong allowed extensions: .png, .jpeg, .jpg"
                return render_template('newentry.html', error = error)

        if pd.isna(pic) or pic == None or pic == '':
            pic ="No Name Submitted"
        
        if isinstance(name, str):
            name = name.strip()
        if pd.isna(name) or name == None or name == '':
            error ="Name cannot be null"
            return render_template('newentry.html', error = error)

        keywords = request.form['keywords']
        details = Details(name = name, state = state, salary= salary, grade = grade, room = room, cno = cno, pic = pic, keywords = keywords)
        query_details = Details.query.filter_by(name=name).first()
        query_pic = Details.query.filter_by(pic = pic).first()
        if query_details == None and (query_pic == None or query_pic.pic == 'No Name Submitted'):
            db.session.add(details)
            db.session.commit()
            return redirect('/')
        else:
            success = None
            error = "An entry with the same name or same image name already exists in the database!!"
            return render_template('newentry.html', error = error)
    return render_template('newentry.html') 


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)