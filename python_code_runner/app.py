from json import dumps

from flask import Flask, render_template, request

from python_code_runner.celery_tasks import process_code_execution

app = Flask(__name__)


@app.route('/', methods=['GET'])
@app.route('/home', methods=['GET'])
def python_runner_page():
    return render_template('python_runner_page.html')


@app.route('/python-handler', methods=['POST'])
def python_runner_handler():
    python_code = request.form.get('python_code')
    task = process_code_execution.delay(python_code)
    return dumps({'task_id': task.id.replace('-', '')}), 202


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8099)
