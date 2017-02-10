#!/usr/bin/python3

import os
from flask import Flask, request, redirect, url_for, render_template, send_from_directory
from werkzeug.utils import secure_filename
import sqlite3
import time
import contextlib
import init
init.main()

app = Flask(__name__)

# site-wide variables
UPLOAD_FOLDER = "uploads/"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
DB_PATH = "database.db"
app.config["DB_PATH"] = DB_PATH


@contextlib.contextmanager
def db_connection():
    """A simple context manager to have a short way
    of connecting to the DB and automatically commiting changes
    and closing the connection."""
    connection = sqlite3.connect(app.config["DB_PATH"])
    c = connection.cursor()
    yield connection, c
    connection.commit()
    connection.close()


@app.route("/", methods=["GET", "POST"])
def hello():
    # handle file upload
    if request.method == "POST":
        # extract file from the request
        file = request.files["file"]
        if file.filename == '':
            # flash('No selected file')
            return redirect(request.url)
        else:
            # choose a filename that can't access system files
            filename = secure_filename(file.filename)
            # choose a target path to save it based on the config
            path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            # connect to the DB
            connection = sqlite3.connect(app.config["DB_PATH"])
            c = connection.cursor()
            # record the file and some metadata
            # null is for the autoincrement id
            c.execute("INSERT INTO files VALUES (NULL,?,?)",
                      (time.strftime("%Y-%m-%d"), path))
            connection.commit()
            connection.close()
            # finally, save the file
            file.save(path)
            # redirect the user to the list of files
            # return redirect(url_for("serve_upload", filename=filename))
            return redirect(url_for("list_files"))
    else:
        return render_template("upload_form.html")


@app.route("/list")
def list_files():
    # connect to DB
    with db_connection() as (_, c):
        # select all records
        c.execute("SELECT * FROM files")
        # get the list of found records
        files = c.fetchall()
    # manipulate DB query results into HTML table
    rows = []
    for f in files:
        # lots of string manipulation
        rows.append(
            "<tr>" + ''.join('<td>{0}</td><td><a href="{1}">{2}</a></td><td><a href="/delete/{2}">DELETE</a></td>'.format(f[1], f[2], os.path.basename(f[2]))) + "</tr>")
    return render_template("file_list.html", file_table="<table>{}</table>".format('\n'.join(rows)))


@app.route("/uploads/<filename>")
def serve_upload(filename):
    # serve the file as a file
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


@app.route("/delete/<filename>")
def delete_upload(filename):
    with db_connection() as (_, c):
        # first get the actual file path of the target filename
        path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        # then remove DB references to it
        c.execute('''DELETE FROM files
            WHERE path=?''', (path,))
    # finally delete the actual file
    os.remove(path)
    # go back to the file list
    return redirect("/list")

if __name__ == "__main__":
    app.run()
