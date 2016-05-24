from flask import *
from sqlalchemy import *
from sqlalchemy.sql import *
from sqlalchemy.orm import sessionmaker
from sql_alchemydeclarative import  Base, User ,Publication, Commentaire , Topic, Reltop

app = Flask(__name__)
app.secret_key = 'iswuygdedgv{&75619892__01;;>..zzqwQIHQIWS'
engine = create_engine('sqlite:///mabase.db')
metadata = MetaData()
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
DBSession.bind = engine
sessiondb = DBSession()
connection = engine.connect()
Error = ''
cree = False
message = ""
logged = []
valeur = 10
topics = []

def getPubs(number=10):
    return sessiondb.query(Publication).order_by(Publication.date.desc()).limit(number)

def getTopics(number=10):
    return sessiondb.query(Topic).limit(number)

@app.route('/')
def index():
    logged = 'logged' in session
    message = ''
    global topics
    topics = []
    if logged:
        message = session['Email']
        pubs = getPubs(valeur)
        for i in pubs:
            print(i.titre)
        topicss = getTopics()
        return render_template('html/Random.html',message=message, logged=logged, pubs=pubs,valeur=valeur,topics=topicss)
    else:
        return render_template('html/index.html',message=message, logged=logged)

@app.route('/change')
def change():
    global valeur
    valeur = request.args.get('valeur', 0, type=int)
    if valeur < 0:
        valeur = 0
    
    #return jsonify(valeur)

@app.route('/login',methods=['POST'])
def login():
    session['Email'] = escape(request.form['Email'])
    session['Password'] = escape(request.form['Password'])
    session['logged'] = False
    person = sessiondb.query(User).filter(or_(User.nom_util == session['Email'],User.email_util == session['Email'])).all()
    for row in person:
        session['logged'] = True
    if session['logged']:
        return redirect('/')
    else:
        session.clear()
        return render_template('html/signer.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/signin')
def signin():
    return render_template('html/signin.html')

@app.route('/register',methods=['POST'])
def register():
    cree = False
    Error = []
    Email = escape(request.form['Email'])
    Pass = escape(request.form['Pass'])
    Name = escape(request.form['Name'])
    person = sessiondb.query(User).filter(or_(User.nom_util == Name,User.email_util == Email)).all()
    for i in person:
        if(i.nom_util == Name):
            Error.append('Nom de utilisateur deja cree')
        if i.email_util ==Email:
            Error.append('Adresse Email deja registre')
        cree = True
    if cree:
        return render_template('html/signin.html',cree=cree,Error=Error)
    else:
        person = User(email_util = Email, nom_util = Name, motpass  = Pass)
        sessiondb.add(person)
        sessiondb.commit()
        session['Email'] = Email
        session['logged'] = True
    return redirect('/')


@app.route('/pub',methods=['POST'])
def pub():
    person = sessiondb.query(User).filter(or_(User.nom_util == session['Email'],User.email_util == session['Email'])).one()
    pub = Publication(cle_util = person.cle_util, auteur = person, titre  = request.form['Titre'], corps = request.form['Corps'] )
    sessiondb.add(pub)
    sessiondb.commit()
    print(pub.cle_pub)
    #pub = sessiondb.query(Publication).filter(cle_util == person.cle_util, auteur == person, titre  == request.form['Titre'], corps == request.form['Corps']).one()
    for i in topics:
        topic = sessiondb.query(Topic).filter(Topic.name_top == i).one()
        relationtopic = Reltop(cle_top = topic.cle_top,cle_pub=pub.cle_pub)
        sessiondb.add(relationtopic)
        sessiondb.commit()
    return redirect('/')

@app.route('/posting/<Iden>')
def posting(Iden):
    publ = sessiondb.query(Publication).filter(Publication.cle_pub == Iden).one()
    comments = sessiondb.query(Commentaire).filter(Commentaire.cle_pub == Iden).all()
    editable = publ.auteur.email_util == session['Email'] or publ.auteur.nom_util == session['Email']
    reltopics = sessiondb.query(Reltop).filter(Reltop.cle_pub == publ.cle_pub).all()
    return render_template('html/posting.html',message= session['Email'], logged = session['logged'],publ = publ,comments = comments , editable=editable ,reltopics=reltopics)

@app.route('/postcomment/<Iden>',methods=['POST'])
def postcomment(Iden):
    print(Iden)
    person = sessiondb.query(User).filter(or_(User.nom_util == session['Email'],User.email_util == session['Email'])).one()
    comm  =  Commentaire(cle_pub = Iden, cle_util=person.cle_util, corps = request.form['Corps'] )
    sessiondb.add(comm)
    sessiondb.commit()
    return redirect('/posting/' + Iden)



@app.route('/getutil')
def getUtil():
    name = request.args.get('message','Vide')
    print(name)
    return jsonify(ches='Putain cela a marche')

@app.route('/getTopTopics')
def getTopTopics():
    topics = sessiondb.query(Topic).all()
    return jsonify(ches=[e.serialize() for e in topics])

@app.route('/searchTopics')
def searchTopics():
    name = request.args.get('message','')
    topics = sessiondb.query(Topic).filter(Topic.name_top.like("%"+name+"%")).all()
    return jsonify(ches=[e.serialize() for e in topics])

@app.route('/upTopics',methods=['GET'])
def upTopics():
    message =  request.args.get('message','Vide')
    global topics
    topics.append(message)
    print(topics)
    print(message)
    return jsonify(ches=1)
    #topcis = message

@app.route('/downTopics',methods=['GET'])
def downTopics():
    global topics
    message =  request.args.get('message','Vide')
    print(topics)
    print(message)
    topics.remove(message)
    return jsonify(ches=1)

@app.route('/createTopic',methods=['GET'])
def createTopic():
    message = request.args.get('message','Vide')
    topicO = Topic(name_top = message)
    sessiondb.add(topicO)
    sessiondb.commit()
    return searchTopics()

@app.route('/change/<Iden>',methods=['POST'])
def changePub(Iden):
    publi = sessiondb.query(Publication).filter(Publication.cle_pub == Iden).one()
    publi.titre = escape(request.form['titre'])
    publi.corps = escape(request.form['Corps'])
    sessiondb.commit()
    return redirect('/posting/' + Iden)

@app.route('/delete/<Iden>')
def deletePub(Iden):
    publi = sessiondb.query(Publication).filter(Publication.cle_pub == Iden).one()
    reltop = sessiondb.query(Reltop).filter(Reltop.cle_pub == Iden).all()
    for i in reltop:
        sessiondb.delete(i)
    sessiondb.delete(publi)
    sessiondb.commit()
    return redirect('/')

@app.route('/topics')
@app.route('/topics/<Iden>')
def topics(Iden=-1):
    pubs = []
    if Iden >= 0:
        pubs = sessiondb.query(Reltop).filter(Reltop.cle_top == Iden).all()
        for i in pubs:
            print(i.topic.name_top)

    return render_template('html/topics.html',message= session['Email'], logged = session['logged'],pubs = pubs)



#@app.route('/_array2python')
#def profile():
#    return json.loads(request.args.get('wordlist'))

if __name__ == '__main__':
  app.run(debug=True)
