from flask import Flask, jsonify, request, render_template
from core.service import midas_engine
from core.models import db
from config import Config
import threading, uuid

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

with app.app_context(): db.create_all()

TASKS = {}

def background_task(tid, p, m, c):
    with app.app_context():
        try:
            res = midas_engine.get_analysis(p, m, c, lambda pct, msg: TASKS.update({tid: {"progress":pct, "message":msg}}))
            TASKS[tid].update({"progress":100, "result":res})
        except Exception as e: TASKS[tid].update({"progress":100, "error":str(e)})

@app.route('/')
def index(): return render_template('index.html')

@app.route('/start_analysis', methods=['POST'])
def start():
    d = request.json
    tid = str(uuid.uuid4())
    TASKS[tid] = {"progress":0, "message":"대기 중..."}
    threading.Thread(target=background_task, args=(tid, d['product'], d['mode'], d['category'])).start()
    return jsonify({"task_id": tid})

@app.route('/status/<tid>')
def status(tid): return jsonify(TASKS.get(tid, {"error":"Not Found"}))

if __name__ == '__main__': app.run(host='0.0.0.0', port=5001, debug=True)