import os
from doctest import debug
from flask import Flask, render_template, request, session, redirect, flash, send_file
from flask.sessions import SecureCookieSession

from werkzeug.utils import secure_filename
from DBConnection import Db
from datetime import datetime


app = Flask(__name__, template_folder='templates', static_url_path='/static/')
UPLOAD_FOLDER = './static'
ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = "asdff"


#login logout signin  section..

@app.route('/')
def h():
    return render_template("login.html")


@app.route('/reg_stud_view_degree')
def reg_stud_view_degree():
    ob = Db()
    q = "select * from degree"
    cdata = ob.select(q)
    return render_template("reg_stud_view_degree.html", cdata=cdata)

@app.route('/reg_stud_form_link')
def reg_stud_form_link():
    iddegree = request.args.get('id')
    session['regiddegree'] = iddegree
    return render_template('sign_up.html')

@app.route('/signup', methods=['post'])
def signup():
    user_id = request.form['user_id']
    ob = Db()
    qry = "select * from login where admin_id='" + user_id + "'"
    admin = ob.selectOne(qry)
    if admin == None:
        qry = "select * from staff_register where user_id='" + user_id + "'"
        staff = ob.selectOne(qry)
        if staff == None:
            qry = "select * from student_register where user_id='" + user_id + "'"
            student = ob.selectOne(qry)
            if student ==None:
                name = request.form['name']
                address = request.form['address']
                email = request.form['email']
                phone = request.form['phone']
                iddegree = session['regiddegree']
                password = request.form['password']
                ob = Db()
                q = "insert into student_register values('" + str(user_id) + "','" + str(name) + "','" + str(address) + "','" + str(email) + "','" + str(phone) + "','" + str(iddegree) + "','" + str(password) + "','pending')"
                ob.insert(q)
                return render_template('login.html')
            else:
                return "<script>alert('please enter a unique userid');window.location='/sign';</script>"
        else:
            return "<script>alert('please enter a unique userid');window.location='/sign';</script>"
    else:
        return "<script>alert('please enter a unique userid');window.location='/sign';</script>"

@app.route('/logout')
def logout():
    return render_template("login.html")

@app.route('/sign')
def sign():
    return render_template("sign_up.html")

@app.route('/login', methods=['post'])
def login():
    user_id = request.form['userid']
    password = request.form['password']

    ob = Db()
    qry = "select * from login where admin_id='" + user_id + "' and password='" + password + "'"
    admin = ob.selectOne(qry)
    if admin ==None:
        qry = "select * from staff_register where user_id='" + user_id + "' and password='" + password + "'"
        staff=ob.selectOne(qry)
        if staff==None:
            qry = "select * from student_register where user_id='" + user_id + "' and password='" + password + "'"
            student = ob.selectOne(qry)
            if student==None:
                return "<script>alert('invalid');window.location='/';</script>"
            else:
                session['userid'] = user_id
                return student_home()


        else:
            session['userid'] = user_id
            return staff_home()
    else:
        session['userid'] = user_id
        return admin_home()




#admin section..

@app.route('/admin_home')
def admin_home():
    return render_template("admin_home.html")


@app.route('/register_degree_link')
def register_degree_link():
    return render_template("admin_register_degree.html")

@app.route('/register_degree', methods=['post'])
def register_degree():
    name = request.form['name']
    txtdes = request.form['txtdes']
    ob = Db()
    q = "insert into degree values(null,'" + name + "','" + txtdes + "')"
    ob.insert(q)
    return view_all_degree()

@app.route('/view_all_degree')
def view_all_degree():
    ob = Db()
    q = "select * from degree"
    cdata = ob.select(q)
    return render_template("admin_view_all_degree.html", cdata=cdata)


@app.route('/delete_degree')
def delete_degree():
    id = request.args.get('id')
    ob = Db()
    q = "delete from degree where iddegree='"+str(id)+"'"
    ob.delete(q)
    return view_all_degree()

@app.route('/edit_degree_link')
def edit_degree():
    id = request.args.get('id')
    ob = Db()
    q = "select * from degree where iddegree='"+str(id)+"'"
    data = ob.selectOne(q)
    return render_template("admin_edit_degree.html", data=data)

@app.route('/admin_update_degree', methods=['post'])
def admin_update_degree():
    id = request.form['id']
    name = request.form['txtname']
    txtdes=request.form['txtdes']
    ob = Db()
    q = "update degree  set name='" + name + "' where iddegree='" + id + "'"
    ob.update(q)
    q = "update degree set description='" + txtdes + "' where iddegree = '" + id + "' "
    ob.update(q)
    return view_all_degree()

@app.route('/view_subject')
def view_subject():
    iddegree = request.args.get('id')
    session['regsubiddegree'] = iddegree
    ob = Db()
    q = "select * from subject where iddegree='" + iddegree + "' "
    data = ob.select(q)
    return render_template('admin_view_subject.html',cdata=data)

@app.route('/register_subject')
def register_subject():
    id = request.args.get('id')
    session['regsubiddegree'] = id
    return render_template('admin_register_subject.html', cdata=id)

@app.route('/register_sub', methods=['post'])
def register_sub():
    iddegree= session['regsubiddegree']
    name = request.form['name']
    semester = request.form['semester']
    ob = Db()
    q = "insert into subject values(null,'" + name + "','" + semester + "','" + iddegree + "')"
    ob.insert(q)
    return admin_view_subjects_from_degree()

@app.route('/admin_view_subjects_from_degree')
def admin_view_subjects_from_degree():
    iddegree = session['regsubiddegree']
    ob = Db()
    q = "select * from subject where iddegree='" + iddegree + "' "
    data = ob.select(q)
    return render_template('admin_view_subject.html', cdata=data)

@app.route('/delete_subject')
def delete_subject():
    idsub = request.args.get('id')
    ob = Db()
    print(id)
    q = "delete from subject where idsubject='"+str(idsub)+"'"
    ob.delete(q)
    return admin_view_subjects_from_degree()  #/admin_view_subjects_from_degree

@app.route('/edit_subject_link')
def edit_subject():
    idsub =  request.args.get('id')
    session['idsub'] = idsub
    ob = Db()
    q = "select * from subject where idsubject ='"+str(idsub)+"'"
    data = ob.selectOne(q)
    return render_template("admin_edit_subject.html", data=data)

@app.route('/admin_update_subject', methods=['post'])
def admin_update_subject():
    id = session['idsub']
    name = request.form['name']
    semester=request.form['semester']
    ob = Db()
    q = "update subject  set name='" + name + "' where idsubject='" + id + "'"
    ob.update(q)
    q = "update subject set semester='" + semester + "' where idsubject = '" + id + "' "
    ob.update(q)
    return admin_view_subjects_from_degree()  #/admin_view_subjects_from_degree

@app.route('/register_staff')
def register_staff():
    return render_template("admin_register_staff.html")

@app.route('/reg_staff', methods=['post'])
def reg_staff():
    userid = request.form['userid']
    name = request.form['name']
    address = request.form['address']
    email = request.form['email']
    phone = request.form['phone']
    password = request.form['password']
    ob = Db()

    qry = "select * from login where admin_id='" + userid + "' "
    admin = ob.selectOne(qry)
    if admin == None:
        qry = "select * from staff_register where user_id='" + userid + "' "
        staff = ob.selectOne(qry)
        if staff == None:
            qry = "select * from student_register where user_id='" + userid + "' "
            student = ob.selectOne(qry)
            if student == None:
                ob = Db()
                q = "insert into staff_register values('" + userid + "','" + name + "','" + address + "','" + email + "','" + phone + "','" + password + "')"
                ob.insert(q)
                return view_all_staff()
            return "<script>alert('please enter a unique userid');window.location='/register_staff';</script>"
        return "<script>alert('please enter a unique userid');window.location='/register_staff';</script>"
    return "<script>alert('please enter a unique userid');window.location='/register_staff';</script>"

@app.route('/view_all_staff')
def view_all_staff():
    ob=Db()
    qry = "select * from staff_register"
    staff = ob.select(qry)

    return render_template("admin_view_all_staff.html", staff=staff)

@app.route('/delete_staff')
def delete_staff():
    id = request.args.get('id')
    ob = Db()
    q = "delete from staff_register where user_id='"+str(id)+"'"
    ob.delete(q)
    return view_all_staff()

@app.route('/edit_staff_link')
def edit_staff():
    id = request.args.get('id')

    ob = Db()
    q = "select * from staff_register where user_id='"+str(id)+"'"
    data = ob.selectOne(q)
    return render_template("admin_edit_staff.html", data=data)

@app.route('/admin_update_staff', methods=['post'])
def admin_update_staff():
    id = request.form['userid']
    name = request.form['name']
    address = request.form['address']
    email = request.form['email']
    phone = request.form['phone']
    password = request.form['password']
    ob = Db()
    qry = "update staff_register  set name='" + name + "' where user_id='" + id + "'"
    ob.update(qry)
    qry = "update staff_register set address='" + address + "' where user_id = '" + id + "' "
    ob.update(qry)
    qry = "update staff_register  set email='" + email + "' where user_id='" + id + "'"
    ob.update(qry)
    qry = "update staff_register set phone='" + phone + "' where user_id = '" + id + "' "
    ob.update(qry)
    qry = "update staff_register  set password='" + password + "' where user_id='" + id + "'"
    ob.update(qry)
    return view_all_staff()

@app.route('/admin_view_approved_files')
def admin_view_approved_files():
    ob= Db()
    q = "select notes.*,degree.name , subject.name as s_name,subject.semester from notes join degree join subject on notes.iddegree=degree.iddegree and notes.idsubject=subject.idsubject where notes.status='approved'"
    data = ob.select(q)
    return render_template('admin_view_approved_files.html', data=data)

@app.route('/approved_delete_file')
def approved_delete_file():
    idnote = request.args.get('id')
    ob = Db()
    q = "delete from notes where idnote='"+str(idnote)+"' "
    ob.delete(q)
    return admin_view_approved_files()

@app.route('/approved_update_file')
def approved_update_file():
    idnote= request.args.get('id')
    session['updateidnote']=idnote
    ob = Db()
    q = " select * from notes where idnote='"+idnote+"'"
    data = ob.selectOne(q)
    return render_template('admin_update_approved_file.html',data=data)

@app.route('/approved_updating_status_file', methods=['post'])
def approved_updating_status_file():
    idnote=session['updateidnote']

    status=request.form['status']
    ob = Db()
    q = "update notes set status='" + status + "' where idnote = '" + idnote + "' "
    ob.update(q)
    return admin_view_approved_files()

@app.route('/approved_download_file')
def approved_download_file():
    filepath = request.args.get('id')
    return send_file(filepath, as_attachment=True)

@app.route('/admin_pending_view_files')
def admin_pending_view_files():
    ob = Db()
    q = "select notes.*,degree.name , subject.name as s_name,subject.semester from notes join degree join subject on notes.iddegree=degree.iddegree and notes.idsubject=subject.idsubject where notes.status='pending'"
    data = ob.select(q)
    return render_template('admin_pending_files.html', data=data)

@app.route('/pending_delete_file')
def pending_delete_file():
    idnote = request.args.get('id')
    ob = Db()
    q = "delete from notes where idnote='"+str(idnote)+"' "
    ob.delete(q)
    return admin_pending_view_files()

@app.route('/pending_download_file')
def pending_download_file():
    filepath = request.args.get('id')
    return send_file(filepath, as_attachment=True)

@app.route('/pending_update_file')
def pending_update_file():
    idnote= request.args.get('id')
    session['updateidnote']=idnote
    ob = Db()
    q = " select * from notes where idnote='"+idnote+"'"
    data = ob.selectOne(q)
    return render_template('admin_update_pending_file.html',data=data)

@app.route('/pending_updating_status_file', methods=['post'])
def pending_updating_status_file():
    idnote=session['updateidnote']

    status=request.form['status']
    ob = Db()
    q = "update notes set status='" + status + "' where idnote = '" + idnote + "' "
    ob.update(q)
    return admin_pending_view_files()

@app.route('/admin_view_approved_students')
def admin_view_approved_students():
    ob= Db()
    q = " select * from student_register where status='approved' "
    data = ob.select(q)
    return render_template('admin_view_approved_students.html', data=data)

@app.route('/approved_update_student')
def approved_update_student():
    user_id= request.args.get('id')
    session['updateuser_id'] = user_id
    ob = Db()
    q = " select * from student_register where user_id='"+user_id+"'"
    data = ob.selectOne(q)
    return render_template('admin_update_approved_student.html',data=data)

@app.route('/approved_updating_status_student', methods=['post'])
def approved_updating_status_student():
    user_id=session['updateuser_id']

    status=request.form['status']
    ob = Db()
    q = "update student_register set status='" + status + "' where user_id = '" + user_id + "' "
    ob.update(q)
    return admin_view_approved_students()

@app.route('/approved_delete_student')
def approved_delete_student():
    user_id =request.args.get('id')
    ob = Db()
    q = "delete from student_register where user_id='"+str(user_id)+"' "
    ob.delete(q)
    return admin_view_approved_students()

@app.route('/admin_pending_students')
def admin_pending_students():
    ob = Db()
    q =" select * from student_register where status='pending'"
    data=ob.select(q)
    return render_template('admin_pending_students.html', data=data)

@app.route('/pending_delete_student')
def pending_delete_student():
    user_id =request.args.get('id')
    ob = Db()
    q = "delete from student_register where user_id='"+str(user_id)+"' "
    ob.delete(q)
    return admin_pending_students()

@app.route('/pending_update_student')
def pending_update_student():
    user_id= request.args.get('id')
    session['updateuser_id'] = user_id
    ob = Db()
    q = " select * from student_register where user_id='"+user_id+"'"
    data = ob.selectOne(q)
    return render_template('admin_update_pending_student.html',data=data)

@app.route('/pending_updating_status_student', methods=['post'])
def pending_updating_status_student():
    user_id= session['updateuser_id']

    status=request.form['status']
    ob = Db()
    q = "update student_register set status='" + status + "' where user_id = '" + user_id + "' "
    ob.update(q)
    return admin_pending_students()






#staff section..

@app.route('/staff_home')
def staff_home():
    return render_template("staff_home.html")

#student section..

@app.route('/student_home')
def student_home():
    ob = Db()
    q ="select * from student_register where user_id='"+session['userid']+"' and status='approved' "
    data=ob.selectOne(q)
    if data==None:
        return "<script>alert('invalid');window.location='/';</script>"
    else:
        ob = Db()
        q = "select * from student_register where user_id='" + session['userid'] + "' and status='approved' "
        data = ob.selectOne(q)
        return render_template("student_home.html",data=data)

@app.route('/staff_view_degree')
def staff_view_degree():
    ob = Db()
    q = "select * from degree"
    cdata = ob.select(q)
    return render_template("staff_view_degree.html", cdata=cdata)

@app.route('/student_view_degree')
def student_view_degree():
    ob = Db()
    q = "select * from degree"
    cdata = ob.select(q)
    return render_template("student_view_degree.html", cdata=cdata)

@app.route('/student_view_degrees')
def student_view_degrees():
    ob = Db()
    q = "select * from degree"
    cdata = ob.select(q)
    return render_template("student_view_degree1.html", cdata=cdata)

@app.route('/staff_view_degrees')
def staff_view_degrees():
    ob = Db()
    q = "select * from degree"
    cdata = ob.select(q)
    return render_template("staff_view_degree1.html", cdata=cdata)
















@app.route('/staff_view_subject')
def staff_view_subject():
    iddegree = request.args.get('id')
    session['uiddegree'] = iddegree
    ob = Db()
    q = "select * from subject where iddegree='" + iddegree + "' "
    data = ob.select(q)
    return render_template('staff_view_subject.html', cdata=data)

@app.route('/student_view_subject', methods=['post'] )
def student_view_subject():
    iddegree = request.form['iddegree']
    semester=request.form['semester']
    session['uiddegree'] = iddegree
    ob = Db()
    q = "select * from subject where iddegree='" + iddegree + "' and semester='" +semester+ "' "
    data = ob.select(q)
    return render_template('student_view_subject.html', cdata=data)

@app.route('/student_view_subjects', methods=['post'] )
def student_view_subjects():
    iddegree = request.form['iddegree']
    semester=request.form['semester']
    session['uiddegree'] = iddegree
    ob = Db()
    q = "select * from subject where iddegree='" + iddegree + "' and semester='" +semester+ "' "
    data = ob.select(q)
    return render_template('student_view_subjects.html', cdata=data)



@app.route('/staff_view_subjects', methods=['post'] )
def staff_view_subjects():
    iddegree = request.form['iddegree']
    semester = request.form['semester']
    session['uiddegree'] = iddegree
    ob = Db()
    q = "select * from subject where iddegree='" + iddegree + "' and semester='" +semester+ "' "
    data = ob.select(q)
    return render_template('staff_view_subjects.html', cdata=data)



















@app.route('/student_upload_file')
def student_upload_file():
    uidsub= request.args.get('id')
    session['uidsub'] = uidsub
    return render_template('student_upload_file.html')

@app.route('/student_uploading', methods=['post'])
def student_uploading():
    iddegree=session['uiddegree']
    idsubject = session['uidsub']
    user_id=session['userid']
    file = request.files['file']
    description=request.form['description']
    if file:
        filename = secure_filename(file.filename)
        print(filename)
        type=filename[-4]+filename[-3]+filename[-2]+filename[-1]
        print(type)
        if type==".pdf":
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            ob = Db()
            q = "insert into notes values(null,'" + iddegree + "','" + idsubject + "','" + user_id + "','static/" + filename + "',curdate(),'pending','"+ description+"')"
            ob.insert(q)
            return "<script>alert('Uploaded succesfully');window.location='/student_cart_files';</script>"
        else:
            return "<script>alert('invalid entry');window.location='/student_view_degree';</script>"


@app.route('/staff_upload_file')
def staff_upload_file():
    uidsub= request.args.get('id')
    session['uidsub'] = uidsub
    return render_template('staff_upload_file.html')

@app.route('/staff_uploading', methods=['post'])
def staff_uploading():
    iddegree=session['uiddegree']
    idsubject = session['uidsub']
    user_id=session['userid']
    file = request.files['file']
    description=request.form['description']
    if file:
        filename = secure_filename(file.filename)
        print(filename)
        type=filename[-4]+filename[-3]+filename[-2]+filename[-1]
        print(type)
        if type==".pdf":
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            ob = Db()
            q = "insert into notes values(null,'" + iddegree + "','" + idsubject + "','" + user_id + "','static/" + filename + "',curdate(),'pending','"+ description+"')"
            ob.insert(q)
            return "<script>alert('Uploaded succesfully');window.location='/staff_cart_files';</script>"
        else:
            return "<script>alert('invalid entry');window.location='/staff_view_degree';</script>"



@app.route('/student_cart_files')
def student_cart_files():
    ob = Db()
    q = "select notes.*,degree.name , subject.name as s_name,subject.semester from notes join degree join subject on notes.iddegree=degree.iddegree and notes.idsubject=subject.idsubject where notes.status='pending'"
    data=ob.select(q)
    ob = Db()
    q = "select notes.*,degree.name , subject.name as s_name,subject.semester from notes join degree join subject on notes.iddegree=degree.iddegree and notes.idsubject=subject.idsubject where notes.status='approved'"
    adata = ob.select(q)
    return render_template('student_cart_files.html', data=data, adata= adata)

@app.route('/staff_cart_files')
def staff_cart_files():
    ob = Db()
    q = "select notes.*,degree.name , subject.name as s_name,subject.semester from notes join degree join subject on notes.iddegree=degree.iddegree and notes.idsubject=subject.idsubject where notes.status='pending'"
    data=ob.select(q)
    ob = Db()
    q = "select notes.*,degree.name , subject.name as s_name,subject.semester from notes join degree join subject on notes.iddegree=degree.iddegree and notes.idsubject=subject.idsubject where notes.status='approved'"
    adata = ob.select(q)
    return render_template('staff_cart_files.html', data=data, adata= adata)












@app.route('/student_view_approved_files')
def student_view_approved_files():
    idsubject = request.args.get('id')
    ob= Db()
    q = "select notes.*,degree.name , subject.name as s_name,subject.semester from notes join degree join subject on notes.iddegree=degree.iddegree and notes.idsubject=subject.idsubject where notes.status='approved' and notes.idsubject='" +idsubject+ "' "
    data = ob.select(q)
    singlerow=ob.selectOne(q)

    return render_template('student_view_approved_files.html', data=data, row=singlerow)


@app.route('/staff_view_approved_files')
def staff_view_approved_files():
    idsubject = request.args.get('id')
    ob= Db()
    q = "select notes.*,degree.name , subject.name as s_name,subject.semester from notes join degree join subject on notes.iddegree=degree.iddegree and notes.idsubject=subject.idsubject where notes.status='approved' and notes.idsubject='" +idsubject+ "' "
    data = ob.select(q)
    singlerow=ob.selectOne(q)

    return render_template('staff_view_approved_files.html', data=data, row=singlerow)



@app.route('/staff_delete_file')
def staff_delete_file():
    idnote = request.args.get('id')
    ob = Db()
    q = "delete from notes where idnote='"+str(idnote)+"' "
    ob.delete(q)
    return staff_cart_files()

@app.route('/student_delete_file')
def student_delete_file():
    idnote = request.args.get('id')
    ob = Db()
    q = "delete from notes where idnote='"+str(idnote)+"' "
    ob.delete(q)
    return student_cart_files()



if __name__ == '__main__':
    app.run(debug=True)

