# Figure Editor plugins

Commands for PhysPlot's built-in Figure Editor. Each time an editor window opens it
loads every `*.py` file here in place (bundled folder first); a file with the same
name in `Documents/PhysPlot/config/figureforge_plugins/` replaces it. Plugins use
PyQt6 for dialogs. A file that fails to import is left out of the menu and named in
the editor's status bar. To have an AI assistant write a plugin, attach
`AI_GUIDE.md` from this folder to the chat.
