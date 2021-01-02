from flask_dropzone import Dropzone
from flask import Flask ,render_template, url_for ,request,redirect,flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
import os
import random
import string
# basedir=os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
# app.config.update(
#     UPLOADED_PATH=os.path.join(basedir,'uploads'),
#     DROPZONE_MAX_FILE_SIZE = 1024,
#     DROPZONE_TIMEOUT = 5*60*1000)
# dropzone = Dropzone(app)


UPLOAD_FOLDER='uploads'
app.secret_key = "Secret_Key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///site.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

db = SQLAlchemy(app)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class News (db.Model) :
    id=db.Column(db.Integer,primary_key=True)
    title=db.Column(db.String(100))
    description=db.Column(db.Text)
    photos = db.relationship('Photo', backref = 'owner')

    def __init__(self,title,description):
         self.title=title
         self.description=description
         
    def __repr__(self):
        return '{title:'+self.title+', description:'+str(self.description)+ '}'     

class Photo(db.Model):
    # id, photoURL, personId
    id = db.Column(db.Integer, primary_key = True)

    photoURL = db.Column(db.String())

    news_id = db.Column(db.Integer, db.ForeignKey('news.id') )

@app.route('/')
def index():
    allnews=News.query.all()
    return render_template ("index.html",alls=allnews)
   
@app.route('/create', methods=['POST','GET'])
def insert():
    if request.method=='POST':
        title = request.form["title"]
        description = request.form['description']
        files = request.files.getlist('photo[]')
        print(files)

        if len(files) == 0:
            flash("No selected file !")
            return redirect(url_for('index'))

        new = News(title, description)

        db.session.add(new)

        for image in files:
            if allowed_file(image.filename):
                filename =  secure_filename(image.filename)
                image.save(os.path.join('static', filename))

                newPhoto = Photo(photoURL = filename, owner = new)
                db.session.add(newPhoto)

        db.session.commit()
        flash("Məlumat daxil oldu. Təşəkkürlər")
        return redirect(url_for('index'))
    else:
        return render_template('create.html')    

@app.route('/delete/<id>/',methods=['GET'])
def delete(id):
    selectednews=News.query.get(id)
    # for image in selectednews.photos:
    #     os.remove(os.path.join('static',image.photoURL))
    db.session.delete(selectednews)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/edit/<int:id>/',methods=['GET', 'POST'])
def edit(id):
    selectednews=News.query.get(id)
    if request.method=='POST':
        selectednews.title=request.form['title']
        selectednews.description=request.form['description']
        files=request.files.getlist('photo[]')
        for file in selectednews.photos:
            os.remove(os.path.join('static', file.photoURL))
            db.session.delete(file)
        for file in files:
            if allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join('static',filename))
                newphoto=Photo(photoURL=filename,owner=selectednews)
                db.session.add(newphoto)
                db.session.commit()
        db.session.commit()    
        return redirect(url_for('index'))
        
    return render_template('edit.html',all=selectednews)



if __name__=='__main__':
    app.run(debug=True)        
