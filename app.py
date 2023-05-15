from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL,MySQLdb
import mysql.connector 
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from config import settings
from config.db_login import db
from smtplib import SMTP
from models.encriptar_contraseña import hash_password
from email.message import EmailMessage
from models import consultas
from flask import Flask
from flask_session import Session
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import webbrowser

db=mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    port=3306,
    database="fania",
)
app = Flask(__name__)


app.secret_key = "secretkey"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
s=URLSafeTimedSerializer("fania")



@app.route('/', methods=['GET','POST'])
def btnreserva():
    if request.method=='POST':
        nombre = request.form['nombre']
        if nombre!="":  
                return redirect(url_for("reserva"))
    return render_template("prueba.html")



@app.get("/")
def inicio():

    return render_template("prueba.html")

@app.get("/login")
def login():

    return render_template("loginadm.html")



@app.get("/reserva")
def reserva():

    return render_template("reserva.html")


@app.route("/login", methods=['GET','POST'])
def loginadm():
   
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']


        
        if consultas.datos_de_login(email=email, password=password) == True:
            session["name"] = request.form.get("password")
            session["email"] = request.form.get("email")
            user = consultas.session_user(email=email, password=password)
            
            session['id'] = user['id']
            
            return redirect(url_for('datos'))
        else:
            flash("Algo salió mal, revisa tus credenciales")

        return render_template("loginadm.html")
    return render_template("loginadm.html")

@app.route("/cita/confirmaremail/<token>")    
def confirmaremail(token):
    try:
        email=s.loads(token, salt="email-confirm", max_age=120)
        consultas.cambiar_estado_de_status(email=email)        
    except SignatureExpired:
        consultas.eliminar_estado_de_status(email=email)
        return "<h1> timeout </h1>"
    return render_template("confirmacion.html", email=email)


@app.get("/login/admin")

def datos(): 
    if not session.get("name"):
        flash('No autentificado')
        return redirect("/login")
    elif not session.get("email"):
        flash('llorindel')
        return redirect("/login")
    data = consultas.mostrar_datos()
         
    return render_template("adm.html",data=data)

@app.route('/cita', methods=['GET','POST'])
def agendar():
    if request.method=='POST':
            username = request.form['username']
            email = request.form['email']    
            celular=request.form['celular']
            fecha1 = request.form['fecha']
            fecha = fecha1.replace("-", "")

            print("Fecha y hora seleccionadas:", fecha)
            
            if celular == "":
                flash("ingrese el número telefónico ")
                return redirect(url_for('cita'))
            if username == "":
                flash("ingrese el nombre ")
                return redirect(url_for('cita'))
            if fecha == "":
                flash("ingrese la fecha ")
                return redirect(url_for('cita'))  
                      
            email = request.form['email']
            original_email = consultas.email_no_repetido(email)
            flag = True

            if (len(original_email)>0):
                flash("El correo ingresado para registrar su cita se encuentra en uso revise nuevamente")
                flag = False
            if flag == False:
                return render_template("cita.html", username=username,celular=celular)


            consultas.insertar_registro_a_db(username=username, email=email, celular=celular,fecha=fecha)


            token = s.dumps(email, salt="email-confirm")
            link = url_for("confirmaremail", token=token, _external=True)

            html_content = """
<html>
<head></head>
<body>
    <h1>Confirmación de correo electrónico</h1>
    <p>Por favor, confirma tu correo electrónico haciendo clic en el siguiente enlace:</p>
    
    <p><a href="{}">Confirmar correo electrónico</a></p>
</body>
</html>
""".format(link)

            msg = MIMEMultipart()
            msg.attach(MIMEText(html_content, 'html'))
            msg['Subject'] = 'Registro de confirmación'
            msg['From'] = settings.SMTP_EMAIL
            msg['To'] = email

            username = settings.SMTP_EMAIL
            password = settings.SMTP_PASSWORD

            server = SMTP("smtp.gmail.com:587")
            server.starttls()
            server.login(username, password)
            server.send_message(msg)
            server.quit()
            flash("Te hemos enviado a tu email un correo de confirmación")
            return redirect(url_for('reserva'))
    else:
            return render_template("cita.html")
@app.get("/cita")
def cita():

    return render_template("cita.html")

@app.route("/eliminar/<int:id>")
def eliminar(id):
    datos=consultas.editar_datos(id=id)
    flash("Dato eliminado exitosamente")

    return redirect(url_for('datos',datos=datos))

@app.route("/finalizar/<int:id>")
def finalizar(id):
    datos=consultas.finalizado(id=id)
    return redirect(url_for('datos',datos=datos))


@app.route("/layout")
def layout():
    session["name"] = None
    session["email"] = None    
    session.clear()
    return redirect("login")





if __name__ == '__main__':
    app.run(debug=True)