
from markdown_it import MarkdownIt
from mdit_py_plugins.front_matter import front_matter_plugin
from mdit_py_plugins.footnote import footnote_plugin
from mdit_py_plugins.container import container_plugin
from mdit_py_plugins.admon import admon_plugin
from mdit_py_plugins.attrs import attrs_block_plugin

md = (
    MarkdownIt("commonmark") # type: ignore
      .use(front_matter_plugin)
      .use(footnote_plugin)
      .use(admon_plugin)
      .use(container_plugin, "plot")
      .use(container_plugin, "center")
      .enable("table")
      .enable("strikethrough")
)