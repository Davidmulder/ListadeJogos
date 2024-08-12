from flask import render_template, request, redirect, session, flash, url_for, send_from_directory
from jogoteca import app, db
from models import Jogos
from helpers import recupera_imagem, deleta_arquivo, FormularioJogo
import time

@app.route('/principal')
def home():
    lista = Jogos.query.order_by(Jogos.id)
    return render_template('principal.html',  jogos=lista)

@app.route('/')
def index():
    lista = Jogos.query.order_by(Jogos.id)
    return render_template('lista.html', titulo='Jogos', jogos=lista)

@app.route('/novo')
def novo():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect(url_for('login', proxima=url_for('novo')))
    form = FormularioJogo()
    return render_template('novo.html', titulo='Novo Jogo', form=form)

@app.route('/criar', methods=['POST',])
def criar():
    form = FormularioJogo(request.form)

    if not form.validate_on_submit():
        return redirect(url_for('novo'))

    nome = form.nome.data
    categoria = form.categoria.data
    console = form.console.data

    jogo = Jogos.query.filter_by(nome=nome).first()

    if jogo:
        flash('Jogo já existente!')
        return redirect(url_for('index'))


        # Trata o upload da imagem
    if 'arquivo' in request.files and request.files['arquivo'].filename != '':
        arquivo = request.files['arquivo']
        upload_path = app.config['UPLOAD_PATH']
        timestamp = time.time()
        nome_arquivo = f'capa{timestamp}.jpg'

        # Salva o arquivo no diretório
        arquivo.save(f'{upload_path}/{nome_arquivo}')



        novo_jogo = Jogos(nome=nome, categoria=categoria, console=console,imagem=nome_arquivo)
        db.session.add(novo_jogo)
        db.session.commit()

    return redirect(url_for('index'))

@app.route('/editar/<int:id>')
def editar(id):
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect(url_for('login', proxima=url_for('editar', id=id)))

    jogo = Jogos.query.filter_by(id=id).first()
    form = FormularioJogo()
    form.nome.data = jogo.nome
    form.categoria.data = jogo.categoria
    form.console.data = jogo.console
    capa_jogo = recupera_imagem(id)
    return render_template('editar.html', titulo='Editando Jogo', id=id, capa_jogo=capa_jogo, form=form)

@app.route('/atualizar', methods=['POST',])
def atualizar():
    form = FormularioJogo(request.form)

    if form.validate_on_submit():

        # Captura o jogo que será atualizado
        jogo = Jogos.query.filter_by(id=request.form['id']).first()

        # Atualiza os campos do jogo
        jogo.nome = form.nome.data
        jogo.categoria = form.categoria.data
        jogo.console = form.console.data

        # Se houver um novo arquivo enviado, processa a imagem
        if 'arquivo' in request.files:
            foto = request.files['arquivo']

        # Define o caminho e o nome do arquivo
        upload_path = app.config['UPLOAD_PATH']
        timestamp = time.time()
        nome_arquivo = f'capa{jogo.id}-{timestamp}.jpg'

       # deleta_arquivo(jogo.id)

        # Salva a nova imagem
        foto.save(f'{upload_path}/{nome_arquivo}')

        # Atualiza o campo 'imagem' do jogo com o nome do arquivo
        jogo.imagem = nome_arquivo

        db.session.add(jogo)
        db.session.commit()



    return redirect(url_for('index'))

@app.route('/deletar/<int:id>')
def deletar(id):
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect(url_for('login'))

    Jogos.query.filter_by(id=id).delete()
    db.session.commit()
    flash('Jogo deletado com sucesso!')

    return redirect(url_for('index'))

@app.route('/uploads/<nome_arquivo>')
def imagem(nome_arquivo):
    return send_from_directory('uploads', nome_arquivo)