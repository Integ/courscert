#!/usr/bin/env python
# coding:utf-8

"""coursera certification crawler"""

import os
import re
import os.path
import sqlite3
import requests
import subprocess
from bs4 import BeautifulSoup
from selenium import webdriver
from flask import Flask, request, jsonify, session, g, redirect, url_for, abort, \
    render_template, flash, send_file
app = Flask(__name__)

DATABASE = 'database.db'


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect('DATABASE')
    rv.row_factory = sqlite3.Row
    return rv


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()
# init_db()


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


@app.route("/")
def index():
    return render_template('index.html')


@app.route('/wall')
def wall():
    certIDs = request.args.getlist('certs')
    certs = []
    total_weeks = 0
    for id in certIDs:
        cert = query_db('select * from certs where cert_id = ?',
                        [id], one=True)
        certDict = cert2Dict(cert)
        certs.append(certDict)
        total_weeks += certDict['weeks']
    return render_template('wall.html', certs=certs, total_weeks=total_weeks)


@app.route('/cert/<cert_id>')
def certPic(cert_id):
    cert_png = 'static/certs/%s.png' % cert_id
    if os.path.isfile(cert_png):
        return send_file(cert_png, mimetype='image/png')
    else:
        cert_pdf = 'https://www.coursera.org/api/certificate.v1/pdf/' + cert_id
        print('Fetching: %s' % cert_pdf)
        r = requests.get(cert_pdf)
        if r.status_code == 200:
            with open('./static/certs/' + cert_id + '.pdf', 'wb') as f:
                f.write(r.content)
            print('Fetched: ./static/certs/%s.pdf' % cert_id)
            print('Converting: %s.pdf to %s.png' % (cert_id, cert_id))
            convert = 'convert -antialias -alpha on -channel rgba -fuzz 5% -density 600 -quality 90 -resize 20%'
            command = "%s ./static/certs/%s.pdf ./static/certs/%s.png" % (
                convert, cert_id, cert_id)
            result = subprocess.call(command, shell=True)
            if result:
                print('Conversion Failed: %s.pdf' % cert_id)
                error = 'conversion failed for %s.pdf' % cert_id
                return jsonify(success=False, error=error)
            else:
                print('Converted: %s.png' % cert_id)
                return send_file(cert_png, mimetype='image/png')
        else:
            return jsonify(success=False, error='Fetch certification failed.')


@app.route('/<cert_id>/fetch')
def fetch(cert_id):
    cert_png = 'static/certs/%s.png' % cert_id
    if os.path.isfile(cert_png):
        return jsonify(success=True, data=cert_png)
    else:
        cert_pdf = 'https://www.coursera.org/api/certificate.v1/pdf/' + cert_id
        print('Fetching: %s' % cert_pdf)
        r = requests.get(cert_pdf)
        if r.status_code == 200:
            with open('./static/certs/' + cert_id + '.pdf', 'wb') as f:
                f.write(r.content)
            print('Fetched: ./static/certs/%s.pdf' % cert_id)
            print('Converting: %s.pdf to %s.png' % (cert_id, cert_id))
            convert = 'convert -antialias -alpha on -channel rgba -fuzz 5% -density 600 -quality 90 -resize 20%'
            command = "%s ./static/certs/%s.pdf ./static/certs/%s.png" % (
                convert, cert_id, cert_id)
            result = subprocess.call(command, shell=True)
            if result:
                print('Conversion Failed: %s.pdf' % cert_id)
                error = 'conversion failed for %s.pdf' % cert_id
                return jsonify(success=False, error=error)
            else:
                print('Converted: %s.png' % cert_id)
                return jsonify(success=True, data=cert_png)
        else:
            return jsonify(success=False, error='Fetch certification failed.')


@app.route('/<cert_id>/crawl')
def getCert(cert_id):
    cert = query_db('select * from certs where cert_id = ?',
                    [cert_id], one=True)
    if cert is None:
        print('Crawling:' + cert_id)
        cert = crawler(cert_id)
        # if isinstance(cert, basestring):
        if isinstance(cert, str):
            return jsonify(success=False, error=cert)
        else:
            certDict = cert2Dict(cert)
            return jsonify(success=True, data=certDict)
    else:
        print('Find cert in datebase: ' + cert_id)
        return jsonify(success=True, data=cert2Dict(cert))


def crawler(cert_id):
    url = 'https://coursera.org/verify/' + cert_id
    print('PhantomJS Rending: ' + url)
    driver = webdriver.PhantomJS()
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    cert_meta = soup.find('div', {'class': 'bt3-col-sm-7'})
    if cert_meta is None:
        return 'the certification is not exist or network error.'
    # print(cert_meta.prettify())
    course_name = cert_meta.find('h4').get_text()
    metas = cert_meta.find_all('p')
    if metas[0].get_text().endswith(u'完成'):
        name_date = metas[0].get_text().split(u'于')
        given_name = name_date[0].split()[0]
        surname = name_date[0].split()[1]
        complete_date = name_date[1].replace(u'完成', '')
    else:
        matchObj = re.match(
            r'Completed by (.*) (.*) on (.*)', metas[0].get_text())
        given_name = matchObj.group(1)
        surname = matchObj.group(2)
        complete_date = matchObj.group(3)
    # print(metas[1].get_text())
    matchObj1 = re.match(
        r'(.*) weeks( of study)?, (.*)-(.*) hours.*', metas[1].get_text())
    weeks = matchObj1.group(1)
    min_hours_a_week = matchObj1.group(3)
    max_hours_a_week = matchObj1.group(4)
    # print(metas[2].get_text())
    # print(metas[3].get_text())
    teacher_name = metas[2].get_text()
    school_name = metas[3].get_text()
    certData = [cert_id, course_name, given_name, surname, complete_date,
                weeks, min_hours_a_week, max_hours_a_week, teacher_name, school_name]
    driver.close()
    print('PhantomJS DONE: %s' % url)
    db = get_db()
    db.execute('insert into certs (cert_id, course_name, given_name, surname, complete_date, weeks, min_hours_a_week, max_hours_a_week, teacher_name, school_name) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
               certData)
    db.commit()
    print('Sqlite Saved: %s' % cert_id)
    print(certData)
    return certData


def cert2Dict(cert):
    last = len(cert)
    certDict = {
        'cert_id': cert[last - 10],
        'course_name': cert[last - 9],
        'given_name': cert[last - 8],
        'surname': cert[last - 7],
        'complete_date': cert[last - 6],
        'weeks': cert[last - 5],
        'min_hours_a_week': cert[last - 4],
        'max_hours_a_week': cert[last - 3],
        'teacher_name': cert[last - 2],
        'school_name': cert[last - 1]
    }
    return certDict

if __name__ == '__main__':
    app.debug = True
    app.run()
    # app.run(host='0.0.0.0')