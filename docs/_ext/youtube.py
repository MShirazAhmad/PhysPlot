"""``youtube`` directive: embed a YouTube video or playlist in the HTML docs.

reStructuredText::

    .. youtube:: JhQnXwG3moY
       :title: The PhysPlot Window

MyST Markdown (``docs/ui/*.md``, written by ``scripts/sync_wiki_to_docs.py``)::

    ```{youtube} PLPkYnHekjU24
    :playlist:
    :title: PhysPlot Basics
    ```

The player is YouTube's privacy-enhanced one (youtube-nocookie.com), 16:9 and at most
720 px wide (``_static/youtube.css``). Builders other than HTML get a link instead.
"""

from __future__ import annotations

from html import escape

from docutils import nodes
from docutils.parsers.rst import Directive, directives
from sphinx import addnodes


class YouTube(Directive):
    required_arguments = 1
    option_spec = {"title": directives.unchanged, "playlist": directives.flag}

    def run(self):
        ident = self.arguments[0]
        title = self.options.get("title") or "PhysPlot video"
        if "playlist" in self.options:
            src = f"https://www.youtube-nocookie.com/embed/videoseries?list={ident}"
            url = f"https://www.youtube.com/playlist?list={ident}"
        else:
            src = f"https://www.youtube-nocookie.com/embed/{ident}"
            url = f"https://youtu.be/{ident}"
        html = (
            f'<div class="youtube-embed"><iframe src="{src}" title="{escape(title)}" loading="lazy" '
            'allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" '
            'referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe></div>'
        )
        fallback = addnodes.only(expr="not html")
        paragraph = nodes.paragraph()
        paragraph += nodes.reference("", f"Video: {title}", refuri=url)
        fallback += paragraph
        return [nodes.raw("", html, format="html"), fallback]


def setup(app):
    app.add_directive("youtube", YouTube)
    app.add_css_file("youtube.css")
    return {"version": "1.0", "parallel_read_safe": True, "parallel_write_safe": True}
