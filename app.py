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
db=mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    port=3306,
    database="fania",
)
app = Flask(__name__)
app.secret_key = "secretkey"
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

@app.get("/reserva")
def reserva():

    return render_template("reserva.html")
@app.get("/login")
def login():

    return render_template("loginadm.html")


@app.route("/login", methods=['GET','POST'])
def loginadm():
   
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        
        if consultas.datos_de_login(email=email, password=password) == True:
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
        email=s.loads(token, salt="email-confirm", max_age=60)
        consultas.cambiar_estado_de_status(email=email)        
    except SignatureExpired:
        consultas.eliminar_estado_de_status(email=email)
        return "<h1> timeout </h1>"
    return "<h1>"+ email + " Registro terminado, a hora puedes iniciar sesión <a href='"+url_for('reserva')+"'>Regresar</a> </h1> "

@app.get("/admin")
def datos(): 
    data = consultas.mostrar_datos()
     
    return render_template("adm.html",data=data)

@app.route('/cita', methods=['GET','POST'])
def agendar():
    if request.method=='POST':
            username = request.form['username']
            email = request.form['email']    
            celular=request.form['celular']
            if celular == "":
                flash("ingrese el número telefónico ")
                return redirect(url_for('cita'))
            if username == "":
                flash("ingrese el nombre ")
                return redirect(url_for('cita'))
            email = request.form['email']
            original_email = consultas.email_no_repetido(email)
            flag = True

            if (len(original_email)>0):
                flash("El correo ingresado para registrar su cita se encuentra en uso revise nuevamente")
                flag = False
            if flag == False:
                return render_template("cita.html", username=username,celular=celular)


            consultas.insertar_registro_a_db(username=username, email=email, celular=celular)


            token=s.dumps(email, salt="email-confirm")
            link = url_for("confirmaremail", token=token, _external=True) 

            msg = EmailMessage()
            msg.set_content("Token de validación: {}".format(link))
            msg["Subject"] = "Registro de confirmación"    
            msg["From"] = settings.SMTP_EMAIL
            msg["To"]  = email
            username = settings.SMTP_EMAIL
            password = settings.SMTP_PASSWORD

            server = SMTP("smtp.gmail.com:587")
            print("Hasta aqui")
            server.starttls()
            server.login(username, password)
            server.send_message(msg)
            server.quit()
            flash("Te hemos enviado a tu email un correo de confirmación. Esto es lo último para crear tu cuenta")
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

@app.route('/layout', methods=["GET","POST"])
def layout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)