from flask import Flask, render_template, request,redirect,url_for
from flask_mysqldb import MySQL
from flask import flash
import pymsgbox
from flask_mail import Mail,Message
app = Flask(__name__)
mail=Mail(app)
mysql = MySQL(app)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Nirmal$31'
app.config['MYSQL_DB'] = 'bank'
app.config['SECRET_KEY']='Bankdetails'
@app.route('/login_up',methods=["GET","POST"])
def login_up():
    dbcur = mysql.connection.cursor()
    if request.method=="GET":
        return render_template("login_up.html")
    elif request.method=="POST":
        IFSC=request.form["IFSC"]
        passw=request.form["password"]
        sql1=("select IFSC from member_details where IFSC=%s")
        sql2=("select password from member_details where IFSC=%s and password=%s")
        dbcur.execute(sql1,(IFSC,))
        c=dbcur.fetchall()
        dbcur.execute(sql2,(IFSC,passw,))
        k=dbcur.fetchall()
        if len(c)==1:
            if len(k)==1:
                return render_template("transfer.html")
            else:
                r=pymsgbox.confirm('Are you forgotten your password','forgotpassword',["Yes","No"])
                if r=="Yes":
                    return render_template("forgot.html")
                else:
                    return redirect(url_for("login_up"))
        else:
            r=pymsgbox.confirm('Do you have Account are not','checking',['sign_up','login_up'])
            if r=="sign_up":
                return render_template("sing_up.html")
            else:
                return redirect(url_for("login_up"))
@app.route('/sign_up',methods=["GET","POST"])
def sign_up():
    dbcur = mysql.connection.cursor()
    if request.method=="GET":
        return render_template("sing_up.html")
    elif request.method=="POST":
        email=request.form["Email"]
        username=request.form["Username"]
        passw=request.form["password"]
        n=request.form["accounts"]
        bankname=[]
        account_no=[]
        IFSC=[]
        bankarea=[]
        balance=[]
        bankname=request.form.getlist("Bankname")
        account_no=request.form.getlist("AccountNumber")
        IFSC=request.form.getlist("IFSCNumber")
        bankarea=request.form.getlist("BankArea")
        balance=request.form.getlist("BalanceMoney")
        #dbcur.execute("create table member_details (IFSC varchar(100) primary key ,username varchar(100),password varchar(100),email varchar(100))")
        #dbcur.execute("create table bankdetails (IFSC varchar(100) primary key,bankname varchar(100),account_no bigint,bankarea varchar(100),balancemoney bigint)")
        for i in IFSC:
            dbcur.execute("insert into member_details (IFSC,username,password,email) values(%s, %s, %s, %s)",(i, username, passw, email))
        n = int(n)
        for i in range(n):
            dbcur.execute("insert into bankdetails(IFSC,bankname,account_no,bankarea,balancemoney) values(%s, %s, %s, %s, %s)",(IFSC[i], bankname[i], account_no[i], bankarea[i], balance[i]))
        mysql.connection.commit()
        dbcur.close()
        pymsgbox.alert("Account is created","Success")
        return render_template("login_up.html")
@app.route('/forgot',methods=["GET","POST"])
def forgot():
    if request.method=="GET":
        return render_template("forgot.html")
    elif request.method=="POST":
        dbcur=mysql.connection.cursor()
        IFSC=request.form["IFSC"]
        np=request.form["password"]
        cp=request.form["cpassword"]
        dbcur.execute("select count(IFSC) from member_details where IFSC=%s",(IFSC,))
        c=dbcur.fetchall()
        if c[0][0] is 1:
            if np==cp:
                c=("update member_details set password=%s where IFSC=%s")
                v=(cp,IFSC,)
                dbcur.execute(c,v)
            else:
                pymsgbox.alert("Two password dose not match","Alert")
                return redirect(url_for("forgot"))
        else:
            pymsgbox.alert("your IFSC number is wrong","Alert")
            return redirect(url_for("forgot"))
        mysql.connection.commit()
        dbcur.close()
        return render_template("login_up.html")
@app.route('/transfer',methods=["GET","POST"])
def transfer():
    dbcur=mysql.connection.cursor()
    if request.method=="GET":
        return render_template("transfer.html")
    elif request.method=="POST":
        IFSC=request.form["IFSC"]
        user=request.form["username"]
        passw=request.form["password"]
        money=request.form["amount"]
        money=int(money)
        fIFSC=request.form["friend"]
        s=("select username,password,balancemoney,email from member_details m,bankdetails b where m.IFSC= %s and b.IFSC= %s")
        dbcur.execute(s,(IFSC,IFSC,))
        c=[]
        for i in dbcur.fetchall():
            for j in i:
                c.append(j)
        s1=("select count(*) from member_details where IFSC= %s")
        dbcur.execute(s1,(fIFSC,))
        s=dbcur.fetchall()
        if s[0][0] is 1:
            if len(c)!=0:
                if user==c[0] or user==c[3]:
                    if passw==c[1]:
                        if money<=c[2]:
                            d=("update bankdetails set balancemoney=balancemoney+%s where IFSC= %s")
                            dbcur.execute(d,(money,fIFSC,))
                            d1=("update bankdetails set balancemoney=balancemoney-%s where IFSC= %s")
                            dbcur.execute(d1,(money,IFSC,))
                        else:
                            pymsgbox.alert("Insufficent Balance","Alert")
                            return redirect(url_for("transfer"))
                    else:
                        pymsgbox.alert("password is wrong", "Alert")
                        return redirect(url_for("transfer"))
                else:
                    pymsgbox.alert("username is wrong","alert")
                    return redirect(url_for("transfer"))
            else:
                pymsgbox.alert("IFSC number is wrong","Alert")
                return redirect(url_for("transfer"))
        else:
            pymsgbox.alert("your friend does not have account","Alert")
            return redirect(url_for("transfer"))
        mysql.connection.commit()
        dbcur.close()
        return render_template("msg.html")
@app.route('/deposit',methods=["GET","POST"])
def deposit():
    dbcur=mysql.connection.cursor()
    if request.method=="GET":
        return render_template("transfer.html")
    elif request.method=="POST":
        IFSC=request.form["IFSC"]
        user=request.form["username"]
        passw=request.form["password"]
        money=request.form["amount"]
        money=int(money)
        s1=("select username,password,email,IFSC from member_details where IFSC=%s")
        dbcur.execute(s1,(IFSC,))
        c=[]
        for i in dbcur.fetchall():
            for j in i:
                c.append(j)
        if c[3]==IFSC:
            if user==c[0] or user==c[2]:
                if passw==c[1]:
                    s2=("update bankdetails set balancemoney=balancemoney+%s where IFSC=%s")
                    dbcur.execute(s2,(money,IFSC,))
                else:
                    pymsgbox.alert("password is wrong","Alert")
                    return redirect(url_for("transfer"))
            else:
                pymsgbox.alert("No user is found","Alert")
                return redirect(url_for("transfer"))
        else:
            pymsgbox.alert("IFSC number is wrong","Alert")
            return redirect(url_for("transfer"))
        mysql.connection.commit()
        dbcur.close()
        return render_template("msg.html")
if __name__ == '__main__':
    app.run(debug=True)
