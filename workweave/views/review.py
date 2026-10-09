"""Review-page composition using package-owned templates and assets."""
from html import escape
from importlib.resources import files
from string import Template


def render_review(project_id, work_id):
    package = files('workweave')
    template = Template(package.joinpath('templates/review.html').read_text(encoding='utf-8'))
    return template.substitute(project_id=escape(project_id, quote=True), work_id=escape(work_id, quote=True),
                               css=package.joinpath('static/review.css').read_text(encoding='utf-8'),
                               js=package.joinpath('static/review.js').read_text(encoding='utf-8'))
