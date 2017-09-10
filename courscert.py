#!/usr/bin/env python
#coding:utf-8

"""get coursera certification pdf2png"""

import requests
import subprocess
import os.path
from flask import Flask
from flask import request
from flask import render_template
from flask import jsonify
app = Flask(__name__)

@app.route("/")
def index():
    return render_template('index.html')

@app.route('/verify/<cert_id>')
def verify(cert_id):
    if os.path.isfile('static/certs/%s.png' % cert_id):
        return jsonify(success=True)

    error = None
    cert_pdf = 'https://www.coursera.org/api/certificate.v1/pdf/' + cert_id

    r = requests.get(cert_pdf)
    if r.status_code == 200:
        with open('./static/certs/' + cert_id + '.pdf', 'wb') as f:
            f.write(r.content)
        convert = 'convert -antialias -alpha on -channel rgba -fuzz 5% -density 600 -quality 90 -resize 20%'
        command = "%s ./static/certs/%s.pdf PNG32:./static/certs/%s.png" % (convert, cert_id, cert_id)
        result = subprocess.call(command, shell=True)
        if result:
            print('Conversion failed for %s.pdf' % cert_id)
            error = 'conversion failed for %s.pdf' % cert_id
            return jsonify(error=error)
        else:
            print('Wrote %s.png' % cert_id)
            return jsonify(success=True)
    else:
        error = 'cert not found'
        return jsonify(error=error)

@app.route('/report')
def report():
    error = None
    name = '%s %s' % (request.args['given_name'], request.args['surname'])
    certs = request.args.getlist('certs')
    return render_template('report.html', name=name, certs=certs)

