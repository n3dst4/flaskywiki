from wiki import app, session
from wiki.models import Version, Page, Tag
from flask import render_template, request, redirect, url_for
from markdown import markdown
from sqlalchemy.orm import eagerload, undefer_group, undefer, lazyload
from sqlalchemy import func, sql


@app.route("/")
def index():
    #SELECT pages.id, pages.name, versions.page_id, max_rev, versions.title
    #FROM (
    #    SELECT page_id, max(rev) as max_rev
    #    FROM versions
    #    GROUP BY page_id
    #    ORDER BY max_rev DESC
    #) s
    #INNER JOIN pages ON s.page_id = pages.id
    #INNER JOIN versions ON s.max_rev = versions.rev;
    
    #max_rev_query = (session.query(Version.page_id, func.max(Version.rev).label("max_rev"))
    #    .group_by(Version.page_id)
    #    .order_by(sql.desc("max_rev"))
    #    .subquery()
    #)
    #    
    #pages = session.query(Page, Version.title).join(Version.page).join(
    #    (max_rev_query, max_rev_query.c.max_rev == Version.rev)
    #)
    
    #pages = Page.query.options(undefer_group("text"))
    pages = Page.query.options(lazyload("tags")).order_by(sql.desc("max_rev"))

    tags = Tag.all()
    return render_template("index.html", tags=tags, pages=pages.all())


@app.route("/view/<name>")
def view(name):
    page = Page.query.filter_by(name=name).first()
    rev = int(request.args.get("rev", "0"))
    version = Version.query.options(undefer("content")).filter_by(page=page).order_by(Version.rev.desc())[rev]
    #version = page.versions[rev]
    title=version.title
    content = markdown(version.content, safe_mode="escape")
    versions = [version.rev for version in page.versions]
    return render_template("wiki.html", rev=rev, title=title, content=content, name=name,
                       versions=versions, version_count=len(versions), tags=[tag.name for tag in page.tags])


@app.route("/edit", methods=["GET"])
@app.route("/edit/<name>", methods=["GET"])
def edit(name=None):
    if "name" in request.args and not name:
        return redirect(url_for("edit", name=request.args.get("name", "")))
    page = Page.query.filter_by(name=name).first()
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
    page = Page.query.options(eagerload("versions")).filter_by(name=name).first()
    if not page:
        page = Page(name)
        session.add(page)
    version = Version(title, markdown)
    page.versions.append(version)
    page.tag_string = request.form.get("tags", "")
    #db.commit()
    return redirect(url_for("view", name=name))


@app.route("/tag/<name>")
def tag(name):
    try:
        pages = Tag.query.filter_by(name=name).first().pages
        pages = [page.name for page in pages]
    except:
        pages = []
    return render_template("tag.html", tag = name, pages=pages)
