#Paquetes y Módulos.
from enum import unique
from flask import Flask, render_template, request,session,redirect,url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
import hashlib
import time


#Configuración inicial
app = Flask(__name__)
app.secret_key = 'EcommerceYugiOhJVBrian'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

#Clases
class Base(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
class User(Base):
    __tablename__ = "User"
    username = db.Column(db.Text,nullable=False, unique=True)
    password = db.Column(db.Integer)
    email = db.Column(db.Text, unique=True, nullable=False)
    rol = db.Column(db.Integer)

class Category(Base):
    __tablename__ = "Category"
    parcial = db.Column(db.Text, unique=True, nullable=False)

class Product(db.Model):
    __tablename__ = "Product"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name= db.Column(db.Text, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    stocks = db.Column(db.Integer, nullable=False)
    popular = db.Column(db.Text)
    picture = db.Column(db.Text)
    category_id = db.Column(db.Integer, db.ForeignKey('Category.id'))

class Orders(Base):
    __tablename__ = "Orders"
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('Product.id'))
    number = db.Column(db.Text, nullable=False)
    price = db.Column(db.Text,nullable=False)
    total = db.Column(db.Text,nullable=False)
    date = db.Column(db.Text,nullable=False)

#Almacenamiento
db.create_all()
product = Product.query.all();
category = Category.query.all();
box=[]

#Salida
@app.route('/exit')
def exit():
    return render_template('exit.html')

#Pagina inicial
@app.route('/')
def index():
    product = Product.query.all();
    category = Category.query.all();
    return render_template('index.html', product= product,category=category)

#Sesiones
@app.route('/sessions')
def sessions():
    session['login_ok'] = False
    session.pop('pack',None)
    session.pop('name',None)
    session.pop('id',None)
    session.pop('rol',None)
    box.clear()
    session['pack']=box
    return redirect(url_for('index'))

#Comprar
@app.route('/add', methods=['GET','POST'])
def add():
    if 'login_ok' in session:
        if (session['login_ok'] == True):
            if request.method == 'GET':
                if (session["rol"] == 1):
                    category = Category.query.all()
                    return render_template('add.html', category=category)
                else:
                    return redirect(url_for('exit'))
            else:
                name = request.form['name']
                price = request.form['price']
                stocks = request.form['stocks']
                picture = request.form['picture']
                categorys = request.form['category']
                new_product = Product(name=name, price=price, stocks=stocks, popular=0, picture=picture, category_id=categorys)
                db.session.add(new_product)
                db.session.commit()
                return redirect(url_for('add'))
        else:
            return redirect(url_for('login'))
    else:
        session['login_ok'] = False
        return redirect(url_for('login'))

#Inicio de sesión
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if 'login_ok' in session:
            if session['login_ok'] == True:
                return redirect(url_for('index'))
            else:
                return render_template('login.html')
        else:
            session['login_ok'] = False
            return redirect(url_for('login'))
    else:
        email = request.form['email']
        password = request.form['pass']
        cifrado = hashlib.sha256(password.encode("utf8")).hexdigest()

        if User.query.filter_by(email=email, password=cifrado).first():
            data = User.query.filter_by(email=email, password=cifrado).first()
            session['login_ok'] = True
            session['name'] = data.username
            session['id'] = data.id
            session['rol'] = data.rol
            session['pack']=box
            return redirect(url_for('index'))
        else:
            return redirect(url_for('login'))

#Pedidos
@app.route('/order')
def order():
    if 'login_ok' in session:
        if(session['login_ok']==True):
            user_id = session["id"]
            order = Orders.query.filter_by(user_id=user_id)
            data=[]
            for i in order:
                product = Product.query.filter_by(id = i.product_id).first()
                add_orders ={
                'Nombre' : str(product.name),
                'Precio' : i.price,
                'Trabajo' : str(product.picture),
                'Numero' : i.number,
                'Total': i.total,
                'Fecha' : i.date
                }
                data.append(add_orders)
            return render_template('orders.html',orders=data, category=category)
        else:
            return redirect(url_for('login'))
    else:
        session['login_ok'] = False
        return redirect(url_for('login'))

#Registro
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        if 'login_ok' in session:
            if session['login_ok'] == True:
                return redirect(url_for('index'))
            else:
                return render_template('register.html')
        else:
            session['login_ok']=False
            return render_template('register.html')
    else:
        try:
            username = request.form['username']
            email = request.form['email']
            password = request.form['pass']
            cifrado = hashlib.sha256(password.encode("utf8")).hexdigest()
            user = User(username=username, password=cifrado, email=email, rol='0')
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('index'))
        except:
            return redirect(url_for('register'))

#Carrito
@app.route('/box_pack')
def box_pack():
    if 'login_ok' in session:
        if(session['login_ok']==True):
            add_car = session["pack"]
            category = Category.query.all()
            return render_template('box.html', add_car=add_car, category=category)
        else:
            return render_template('login.html')
    else:
        session['login_ok'] = False
        return redirect(url_for('login'))

#Detalles del producto
@app.route('/ns/<id>')
def ns(id):
    nsDetail = Product.query.filter_by(id=id).first()
    category = Category.query.filter_by(id=nsDetail.category_id).first()
    categorys = Category.query.all()
    return render_template('ns.html', nsDetail=nsDetail, category=category, categorys=categorys)

#Eliminar del carrito
@app.route('/nsDelete/<id>')
def nsDelete(id):
    if 'login_ok' in session:
        if(session['login_ok']==True):
            pack=[]
            pack= session["pack"]
            box.clear()
            for i in pack:
                if str(i['id'])!=str(id) :
                    box.append(i)
            session["pack"] = box
            return render_template('box.html',ad_car=session["pack"])
        else:
            return redirect(url_for('login'))
    else:
        session['login_ok'] = False
        return redirect(url_for('login'))

#Actualizar producto
@app.route('/nsUpdate/<id>',methods=['POST','GET'])   
def nsUpdate(id):
    if 'login_ok' in session:
        if(session['login_ok']==True):
            if request.method == 'GET':
                return redirect(url_for('index'))
            else:
                numero = int(request.form['numero'])
                pack=[]
                pack = session["pack"]
                box.clear()
                for i in pack:
                    if str(i['id'])==str(id):
                        price = int(i['Precio'])
                        cuenta = numero * 0.99
                        total = (price * numero)+cuenta
                        i['numero']=str(numero)
                        i['total']=str(total)
                    box.append(i)
                session["pack"] = box
                return redirect(url_for('box_pack'))
        else:
            return redirect(url_for('login'))
    else:
        session['login_ok'] = False
        return redirect(url_for('login'))

#Vaciar carrito
@app.route('/cartbosalt',methods = ['GET'])
def cartbosalt():
    if 'login_ok' in session:
        if(session['login_ok']==True):
            box.clear()
            session["pack"] = box
            return redirect(url_for('box_pack'))
        else:
            return redirect(url_for('login'))
    else:
        session['login_ok'] = False
        return redirect(url_for('login'))

#Verificar
@app.route('/verify')
def verify():
    if 'login_ok' in session:
        if(session['login_ok']==True):
            kid = session['id']
            box=session["pack"]
            for i in box:
                product_id = int(i["id"])
                numero = str(i["Numero"])
                products = Product.query.filter_by(id=product_id).first()
                products.popular = int(numero)
                products.stocks = int(numero)
                db.session.add(products)
                db.session.commit()
                date = str(time.strftime("%x")+"-"+time.strftime("%X"))
                price = i["Precio"]
                total = i["Total"]
                order = Orders(user_id=kid, product_id=product_id, number=numero, date=date, price=price,total=total)
                db.session.add(order)
                db.session.commit()
            box.clear()
            session["pack"]=box
            return redirect(url_for('box_pack'))
        else:
            return redirect(url_for('login'))
    else:
        session['login_ok'] = False
        return redirect(url_for('login'))

#Agregar al carrito
@app.route('/add_car/<id>')
def add_car(id):
    if 'login_ok' in session:
        if(session['login_ok']==True):
            product = Product.query.filter_by(id=id).first()
            cont=False
            box = session["pack"]
            for i in box:
                if str(i['id'])==str(id):
                    cont=True
            if box==[]:
                numero=1
                cuenta = numero * 0.99
                precio = int(product.price) + cuenta
                total = numero * precio
                add_car = {
                    'id': product.id,
                    'Nombre': product.name,
                    'Precio': precio,
                    'Imagen': product.picture,
                    'Numero': numero,
                    'Total':total
                }
                box.append(add_car)
            elif cont==True:
                pack=[]
                for j in box:
                    if str(j['id'])==str(id):
                        numero=int(j["Numero"])
                        numero += 1
                        cuenta= numero * 0.99
                        precio = int(j['Precio'])
                        total = (precio * numero) + cuenta
                        j['numero']=str(numero)
                        j['total']=str(total)
                        pack.append(j)
                    else:
                        pack.append(j)
            else:
                numero=1
                cuenta = numero * 0.99
                precio = int(product.price) + cuenta
                total = numero * precio

                add_car= {
                    'id': product.id,
                    'Nombre': product.uismi,
                    'Precio': precio,
                    'Imagen': product.picture,
                    'Numero': numero,
                    'Total':total
                }
                box.append(add_car)
            session["pack"] = box
            return redirect(url_for('box_pack'))
        else:
            return redirect(url_for('login'))
    else:
        session['login_ok'] = False
        return redirect(url_for('login'))

#Categorias
@app.route('/category/<category_id>')
def category_id(category_id):
    data = Product.query.filter_by(category_id=category_id).order_by(desc(Product.popular))
    category = Category.query.all()
    return render_template('index.html', category=category, product=data)

#Actualizar producto agregado
@app.route('/update', methods=['GET','POST'])
def update():
    if 'login_ok' in session:
        if (session['login_ok'] == True):
            if request.method == 'GET':
                if (session["rol"] == 1):
                    categorias = Category.query.all()
                    productos = Product.query.all()
                    return render_template('update.html', productos=productos, categorias=categorias);
                else:
                    return redirect(url_for('exit'))
            else:
                ns = Product.query.filter_by(id=request.form['update']).first()
                ns.name = request.form['name']
                ns.price = request.form['price']
                ns.stocks = request.form['stocks']
                ns.picture= request.form['picture']
                ns.category_id = request.form['category']
                db.session.add(ns)
                db.session.commit()
                return redirect(url_for('update'))
        else:
            return redirect(url_for('login'))
    else:
        session['login_ok'] = False
        return redirect(url_for('login'))

#ya
#Eliminar producto agregado
@app.route('/delete',methods=['GET','POST'])
def delete():
    if 'login_ok' in session:
        if(session['login_ok']==True):
            if request.method == 'GET':
                if(session["rol"] == 1):
                    category = Category.query.all()
                    product = Product.query.all()
                    return render_template('delete.html',product=product, category=category)
                else:
                    return redirect(url_for('exit'))
            else:
                nssec = request.form['nssec']
                ns = Product.query.filter_by(id=nssec).first()
                db.session.delete(ns)
                db.session.commit()
                return redirect(url_for('delete'))
        else:
            return redirect(url_for('login'))
    else:
        session['login_ok'] = False
        return redirect(url_for('login'))


#Arranque
if __name__ == '__main__':
    app.run(debug=True)