from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import requests

main = Blueprint('main', __name__)

API = 'http://127.0.0.1:5000'


def api(path, method='GET', data=None, token=None):
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    try:
        if method == 'POST':
            r = requests.post(API + path, json=data, headers=headers)
        else:
            r = requests.get(API + path, headers=headers)
        return r.json()
    except Exception:
        return {}


# ── AUTH ──────────────────────────────────────────────────────────────────────

@main.route('/')
def index():
    if session.get('token'):
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')


@main.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('token'):
        return redirect(url_for('main.dashboard'))
    if request.method == 'POST':
        r = api('/auth/login', 'POST', {
            'username': request.form['username'],
            'password': request.form['password']
        })
        if r.get('access_token'):
            session['token'] = r['access_token']
            session['username'] = request.form['username']
            return redirect(url_for('main.dashboard'))
        flash(r.get('msg', 'Login failed.'), 'error')
    return render_template('login.html')


@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        r = api('/auth/register', 'POST', {
            'username': request.form['username'],
            'password': request.form['password']
        })
        if r.get('msg') == 'User registered':
            flash('Account created! Please sign in.', 'success')
            return redirect(url_for('main.login'))
        flash(r.get('msg', 'Registration failed.'), 'error')
    return render_template('register.html')


@main.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.login'))


# ── DASHBOARD ─────────────────────────────────────────────────────────────────

@main.route('/dashboard')
def dashboard():
    if not session.get('token'):
        return redirect(url_for('main.login'))
    token = session['token']

    plan = api('/planner/plan', token=token)
    score_data = api('/ai/readiness', token=token)

    days_left   = plan.get('days_left')
    daily_plan  = plan.get('daily_plan', [])
    topic_count = len(daily_plan)
    readiness_score = score_data.get('readiness_score')

    return render_template('dashboard.html',
        days_left=days_left,
        daily_plan=daily_plan,
        topic_count=topic_count,
        readiness_score=readiness_score
    )


# ── PLANNER ───────────────────────────────────────────────────────────────────

@main.route('/planner')
def planner():
    if not session.get('token'):
        return redirect(url_for('main.login'))
    token = session['token']

    plan_data = api('/planner/plan', token=token)
    # Fetch topics for chip display (reuse plan data)
    topics_raw = plan_data.get('daily_plan', [])
    topics = [type('T', (), {'name': t['topic']})() for t in topics_raw]

    exam = None  # Extend later if you add a GET /planner/exam endpoint

    return render_template('planner.html',
        plan=plan_data if 'days_left' in plan_data else None,
        topics=topics,
        exam=exam
    )


@main.route('/planner/exam', methods=['POST'])
def add_exam():
    if not session.get('token'):
        return redirect(url_for('main.login'))
    r = api('/planner/exam', 'POST', {
        'exam_date': request.form['exam_date'],
        'daily_hours': float(request.form['daily_hours'])
    }, token=session['token'])
    if r.get('exam_date'):
        flash(f"Exam saved for {r['exam_date']}!", 'success')
    else:
        flash(r.get('msg', 'Failed to save exam.'), 'error')
    return redirect(url_for('main.planner'))


@main.route('/planner/topic', methods=['POST'])
def add_topic():
    if not session.get('token'):
        return redirect(url_for('main.login'))
    r = api('/planner/topic', 'POST', {
        'name': request.form['name']
    }, token=session['token'])
    if r.get('topic'):
        flash(f"Topic '{r['topic']}' added!", 'success')
    else:
        flash(r.get('msg', 'Failed to add topic.'), 'error')
    return redirect(url_for('main.planner'))


# ── PROGRESS ──────────────────────────────────────────────────────────────────

@main.route('/progress')
def progress():
    if not session.get('token'):
        return redirect(url_for('main.login'))
    from models import StudySession
    from flask_jwt_extended import decode_token
    try:
        data = decode_token(session['token'])
        user_id = data['sub']
        sessions = StudySession.query.filter_by(user_id=user_id).all()
    except Exception:
        sessions = []
    return render_template('progress.html', sessions=sessions)


@main.route('/progress/log', methods=['POST'])
def log_session():
    if not session.get('token'):
        return redirect(url_for('main.login'))
    from models import db, StudySession
    from flask_jwt_extended import decode_token
    try:
        data = decode_token(session['token'])
        user_id = data['sub']
        s = StudySession(
            actual_hours=float(request.form['actual_hours']),
            user_id=user_id
        )
        db.session.add(s)
        db.session.commit()
        flash('Session logged!', 'success')
    except Exception as e:
        flash('Failed to log session.', 'error')
    return redirect(url_for('main.progress'))


# ── AI INSIGHTS ───────────────────────────────────────────────────────────────

@main.route('/ai-insights')
def ai_insights():
    if not session.get('token'):
        return redirect(url_for('main.login'))
    r = api('/ai/readiness', token=session['token'])
    score = r.get('readiness_score')
    return render_template('ai_insights.html', score=score)