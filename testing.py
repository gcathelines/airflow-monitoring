from flask import Flask, redirect

app = Flask(__name__)

@app.route('/redirect')
def redir():
    return redirect("http://w49m1:s3cr3t@localhost:1337/admin", code=302)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)