#! /usr/bin/env python

from flask import Flask, render_template, request, redirect
from markdown import markdown
from pdb import set_trace


################################################################################
## App object

app = Flask(__name__)


################################################################################
## Model

from flask_sqla_models import Session as db_session, Version, Page, Tag

################################################################################
## Pages

@app.route("/")
def index():
    pages = list(db_session.query(Page).order_by(Page.name))
    tags = Tag.all()
    return render_template("index.html", pages=pages, tags=tags)


@app.route("/view/<name>")
def view(name):
    page = db_session.query(Page).filter_by(name=name).first()
    rev = int(request.args.get("rev", "-1"))
    if rev == -1:
        version = page.versions[0]
    else:
        version = db_session.query(Version).filter_by(page=page, rev=rev
                  ).first()
    title=version.title
    content = markdown(version.content, safe_mode="escape")
    versions = (version.rev for version in page.versions)
    return render_template("wiki.html", rev=rev, title=title, content=content, name=name,
                       versions=versions, tags=page.tag_list())


@app.route("/edit", methods=["GET"])
@app.route("/edit/<name>", methods=["GET"])
def edit(name=None):
    if "name" in request.args and not name:
        return redirect("/edit/" + request.args.get("name", ""))
    page = db_session.query(Page).filter_by(name=name).first()
    if not page:
        markdown=""
        title=""
        tags=""
    else:
        title = page.versions[0].title
        markdown = page.versions[0].content
        tags = page.tag_string
    return render_template("edit.html", name=name, markdown=markdown, title=title, tags=tags)


@app.route("/edit/<name>", methods=["POST"])
def save_edit(name):
    title = request.form.get("title", "")
    if not title:
        return redirect("/edit/" + name)
    markdown = request.form.get("markdown", "")
    page = db_session.query(Page).filter_by(name=name).first()
    if not page:
        page = Page(name)
        db_session.add(page)
    version = Version(title, markdown)
    page.versions.append(version)
    page.tag_string = request.form.get("tags", "")
    db_session.commit()
    return redirect("/view/" + name)


@app.route("/tag/<name>")
def tag(name):
    try:
        pages = db_session.query(Tag).filter_by(name=name).first().pages
        pages = [page.name for page in pages]
    except:
        pages = []
    return render_template("tag.html", tag = name, pages=pages)


if __name__ == "__main__": app.run(debug=True, host="0.0.0.0", port=8000)











































