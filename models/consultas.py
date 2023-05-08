from config.db_login import db


def insertar_registro_a_db(username, email, celular):
    cursor = db.cursor(buffered=True)
    cursor.execute("INSERT INTO agendar (nombre, email, celular) values (%s,%s,%s)",(
    username, 
    email, 
    celular, 
    ))
    cursor.close()
def cambiar_estado_de_status(email):
    cursor = db.cursor(buffered=True)
    cursor.execute("UPDATE agendar SET status='1' WHERE email='"+email+"'"),(
    email,
    )
    cursor.close()


def email_no_repetido(email):
    cursor = db.cursor(dictionary=True, buffered=True)
    cursor.execute("SELECT * FROM agendar WHERE email = %s",(
        email,
    ))
    email = cursor.fetchall()
    print(email)
    return email

def datos_de_login(email, password):
    cursor = db.cursor(buffered=True)
    
    cursor.execute("SELECT * FROM adm WHERE email = %s and contraseña = %s ",(
        email,
        password,
    ))
    vae = cursor.fetchone()
    cursor.close()  
    variabl = False
    if vae != None:
        variabl=True
    return variabl

def session_user(email, password):
    cursor = db.cursor(dictionary=True, buffered=True)
    cursor.execute("SELECT * FROM adm WHERE email = %s and contraseña = %s ",(
        email,
        password,
    ))
    vae = cursor.fetchone()
    cursor.close()  
    return vae
def mostrar_productos_usuario():
    cursor = db.cursor(buffered=True, dictionary=True)
    cursor.execute("SELECT * FROM agendar WHERE status='1'")
    products = cursor.fetchall()
    cursor.close()
    return products
def mostrar_datos():
    cursor = db.cursor(buffered=True, dictionary=True)
    cursor.execute("SELECT * FROM agendar")
    resultados = cursor.fetchall()
    cursor.close()
    return resultados

def editar_datos(id):
    cursor = db.cursor(buffered=True)
    cursor.execute(" DELETE  FROM agendar WHERE id = %s ",(
        id,
    ))

    datos = cursor.fetchone()
    cursor.close()  
    return datos
def finalizado(id):
    cursor = db.cursor(buffered=True)
    cursor.execute(" UPDATE agendar SET finalizado='si' WHERE id = %s ",(
        id,
    ))

    datos = cursor.fetchone()
    cursor.close()  
    return datos  