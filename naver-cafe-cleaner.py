from flask import Flask, session, request, render_template, redirect, url_for
from flask_kvsession import KVSessionExtension
from core.naver import get_naver_session, get_cafes, remove_cafe
from simplekv.memory import DictStore

app = Flask(__name__)
app.secret_key = 'You know nothing, Johann Schnee!'

store = DictStore()
KVSessionExtension(store, app)


@app.route('/')
def index():
    try:
        return render_template('main.html', naver_username=session['naver_username'], cafes=session['cafes'])
    except KeyError:
        return render_template('login.html', message='먼저 네이버에 로그인해주세요. (ID/PW는 저장되지 않습니다.)')


@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    naver = get_naver_session(username, password)
    if naver is not None:
        session['logged_in'] = True
        session['naver_username'] = username
        session['cafes'] = get_cafes(naver)
        return redirect(url_for('index'))
    else:
        return render_template('login.html', message='로그인 실패! 네이버 ID/PW를 다시 확인해주세요.')


@app.route('/logout')
def logout():
    session['logged_in'] = False
    del session['naver_username']
    del session['cafes']
    return redirect(url_for('index'))


@app.route('/confirm', methods=['POST'])
def confirm():
    club_ids = [int(i) for i in request.form.getlist('club_id')]
    cafes_to_remove = [c for c in session['cafes'] if c.club_id in club_ids]
    return render_template('confirm.html', naver_username=session['naver_username'], cafes=cafes_to_remove)


@app.route('/clean', methods=['POST'])
def clean():
    club_ids = [int(i) for i in request.form.getlist('club_id')]
    cafes_to_remove = [c for c in session['cafes'] if c.club_id in club_ids]  # Same procedure as above
    naver = get_naver_session(session['naver_username'], request.form.get('password'))
    result = []
    for cafe in cafes_to_remove:
        result.append({'cafe': cafe, 'result': remove_cafe(naver, cafe)})
    # Update cafes list
    session['cafes'] = get_cafes(naver)
    return render_template('result.html', result=result)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
