#!/usr/bin/env python
# coding:utf-8

"""get coursera certification pdf2png"""

import os
import re
import os.path
import sqlite3
import requests
import subprocess
from bs4 import BeautifulSoup
from selenium import webdriver
from flask import Flask, request, jsonify, session, g, redirect, url_for, abort, \
    render_template, flash

app = Flask(__name__)

DATABASE = 'database.db'


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect('DATABASE')
    rv.row_factory = sqlite3.Row
    return rv


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()
# init_db()


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route("/")
def index():
    return render_template('index.html')


@app.route('/verify/<cert_id>')
def verify(cert_id):
    cur = g.db.execute('select * from certs where cert_id = ?', (cert_id,))
    certData = cur.fetchAll()
    print(certData)
    if len(certData):
        return jsonify(success=True, data=certData)
    else:
        certData = crawler(cert_id)
        return jsonify(error=certData)


@app.route('/report')
def report():
    error = None
    name = '%s %s' % (request.args['given_name'], request.args['surname'])
    certIDs = request.args.getlist('certs')
    certs = []
    for id in certIDs:
        cur = g.db.execute('select * from certs where cert_id= ? ', (id,))
        cert = [dict(id=row[0], cert_id=row[1]) for row in cur.fetchall()]
        certs.append(cert)
    return render_template('report.html', name=name, certs=certs)


def crawler(cert_id):
    db = get_db()
    cur = g.db.execute('select * from certs where cert_id = ?', (cert_id,))
    certData = cur.fetchAll()
    print(certData)
    if len(certData) != 0:
        return certData

    url = 'https://coursera.org/verify/' + cert_id
    print('PhantomJS: ' + url)
    driver = webdriver.PhantomJS()
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    cert_meta = soup.find('div', {'class': 'bt3-col-sm-7'})
    course_name = cert_meta.find('h4').get_text()
    metas = cert_meta.find_all('p')

    matchObj = re.match(r'Completed by (.*) (.*) on (.*)', metas[0].get_text())
    given_name = matchObj.group(1)
    surname = matchObj.group(2)
    complete_date = matchObj.group(3)

    matchObj1 = re.match(
        r'(.*) weeks, (.*)-(.*) hours per week', metas[1].get_text())
    weeks = matchObj1.group(1)
    min_hours_a_week = matchObj1.group(2)
    max_hours_a_week = matchObj1.group(3)

    teacher_name = metas[2].get_text()
    school_name = metas[3].get_text()
    certData = [cert_id, course_name, given_name, surname, complete_date,
                weeks, min_hours_a_week, max_hours_a_week, teacher_name, school_name]
    driver.close()

    error = None
    cert_pdf = 'https://www.coursera.org/api/certificate.v1/pdf/' + cert_id
    print('fetch %s.pdf' % cert_id)
    r = requests.get(cert_pdf)
    if r.status_code == 200:
        with open('./static/certs/' + cert_id + '.pdf', 'wb') as f:
            f.write(r.content)
        convert = 'convert -antialias -alpha on -channel rgba -fuzz 5% -density 600 -quality 90 -resize 20%'
        command = "%s ./static/certs/%s.pdf PNG32:./static/certs/%s.png" % (
            convert, cert_id, cert_id)
        result = subprocess.call(command, shell=True)
        if result:
            print('Conversion failed for %s.pdf' % cert_id)
            error = 'conversion failed for %s.pdf' % cert_id
            return error
        else:
            print('Wrote %s.png' % cert_id)
            db.execute('insert into certs (cert_id, course_name, given_name, surname, complete_date, weeks, min_hours_a_week, max_hours_a_week, teacher_name, school_name) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                       certData)
            db.commit()
            return certData
    else:
        error = 'cert not found'
        return error
