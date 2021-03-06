# -*- coding: utf-8 -*-
#
# Picard, the next-generation MusicBrainz tagger
# Copyright (C) 2007 Lukáš Lalinský
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

import os.path
from functools import partial
from PyQt4 import QtCore, QtGui
from picard import config, log
from picard.util import icontheme
from picard.ui.options import OptionsPage, register_options_page
from picard.ui.ui_options_interface import Ui_InterfaceOptionsPage
from picard.ui.util import enabledSlot
from picard.const import UI_LANGUAGES
import operator
import locale


class InterfaceOptionsPage(OptionsPage):

    NAME = "interface"
    TITLE = N_("User Interface")
    PARENT = None
    SORT_ORDER = 80
    ACTIVE = True
    SEPARATOR = u'—'*5
    TOOLBAR_BUTTONS = {
        'add_directory_action': {
            'label': N_(u'Add Folder'),
            'icon': 'folder'
        },
       'add_files_action': {
            'label': N_(u'Add Files'),
            'icon': 'document-open'
        },
       'cluster_action': {
            'label': N_(u'Cluster'),
            'icon': 'picard-cluster'
        },
       'autotag_action': {
            'label': N_(u'Lookup'),
            'icon': 'picard-auto-tag'
        },
       'analyze_action': {
            'label': N_(u'Scan'),
            'icon': 'picard-analyze'
        },
       'browser_lookup_action': {
            'label': N_(u'Lookup in Browser'),
            'icon': 'lookup-musicbrainz'
        },
       'save_action': {
            'label': N_(u'Save'),
            'icon': 'document-save'
        },
       'view_info_action': {
            'label': N_(u'Info'),
            'icon': 'picard-edit-tags'
        },
       'remove_action': {
            'label': N_(u'Remove'),
            'icon': 'list-remove'
        },
       'submit_acoustid_action': {
            'label': N_(u'Submit AcoustIDs'),
            'icon': 'acoustid-fingerprinter'
        },
       'play_file_action': {
            'label': N_(u'Open in Player'),
            'icon': 'play-music'
        },
       'cd_lookup_action': {
            'label': N_(u'Lookup CD...'),
            'icon': 'media-optical'
        },
    }
    ACTION_NAMES = set(TOOLBAR_BUTTONS.keys())
    options = [
        config.BoolOption("setting", "toolbar_show_labels", True),
        config.BoolOption("setting", "toolbar_multiselect", False),
        config.BoolOption("setting", "builtin_search", False),
        config.BoolOption("setting", "use_adv_search_syntax", False),
        config.BoolOption("setting", "quit_confirmation", True),
        config.TextOption("setting", "ui_language", u""),
        config.BoolOption("setting", "starting_directory", False),
        config.TextOption("setting", "starting_directory_path", ""),
        config.ListOption("setting", "toolbar_layout", [
            'add_directory_action',
            'add_files_action',
            'separator',
            'cluster_action',
            'separator',
            'autotag_action',
            'analyze_action',
            'browser_lookup_action',
            'separator',
            'save_action',
            'view_info_action',
            'remove_action',
            'separator',
            'cd_lookup_action',
            'separator',
            'submit_acoustid_action',
        ]),
    ]

    def __init__(self, parent=None):
        super(InterfaceOptionsPage, self).__init__(parent)
        self.ui = Ui_InterfaceOptionsPage()
        self.ui.setupUi(self)
        self.ui.ui_language.addItem(_('System default'), '')
        language_list = [(l[0], l[1], _(l[2])) for l in UI_LANGUAGES]
        for lang_code, native, translation in sorted(language_list, key=operator.itemgetter(2),
                                                     cmp=locale.strcoll):
            if native and native != translation:
                name = u'%s (%s)' % (translation, native)
            else:
                name = translation
            self.ui.ui_language.addItem(name, lang_code)
        self.ui.starting_directory.stateChanged.connect(
            partial(
                enabledSlot,
                self.ui.starting_directory_path.setEnabled
            )
        )
        self.ui.starting_directory.stateChanged.connect(
            partial(
                enabledSlot,
                self.ui.starting_directory_browse.setEnabled
            )
        )
        self.ui.starting_directory_browse.clicked.connect(self.starting_directory_browse)
        self.ui.add_button.clicked.connect(self.add_to_toolbar)
        self.ui.insert_separator_button.clicked.connect(self.insert_separator)
        self.ui.remove_button.clicked.connect(self.remove_action)
        self.ui.up_button.clicked.connect(partial(self.move_item, 1))
        self.ui.down_button.clicked.connect(partial(self.move_item, -1))
        self.ui.toolbar_layout_list.currentRowChanged.connect(self.update_buttons)
        self.ui.toolbar_layout_list.setDragDropMode(QtGui.QAbstractItemView.DragDrop)
        self.ui.toolbar_layout_list.setDefaultDropAction(QtCore.Qt.MoveAction)

    def load(self):
        self.ui.toolbar_show_labels.setChecked(config.setting["toolbar_show_labels"])
        self.ui.toolbar_multiselect.setChecked(config.setting["toolbar_multiselect"])
        self.ui.builtin_search.setChecked(config.setting["builtin_search"])
        self.ui.use_adv_search_syntax.setChecked(config.setting["use_adv_search_syntax"])
        self.ui.quit_confirmation.setChecked(config.setting["quit_confirmation"])
        current_ui_language = config.setting["ui_language"]
        self.ui.ui_language.setCurrentIndex(self.ui.ui_language.findData(current_ui_language))
        self.ui.starting_directory.setChecked(config.setting["starting_directory"])
        self.ui.starting_directory_path.setText(config.setting["starting_directory_path"])
        self.populate_action_list()
        self.ui.toolbar_layout_list.setCurrentRow(0)
        self.update_buttons()

    def save(self):
        config.setting["toolbar_show_labels"] = self.ui.toolbar_show_labels.isChecked()
        config.setting["toolbar_multiselect"] = self.ui.toolbar_multiselect.isChecked()
        config.setting["builtin_search"] = self.ui.builtin_search.isChecked()
        config.setting["use_adv_search_syntax"] = self.ui.use_adv_search_syntax.isChecked()
        config.setting["quit_confirmation"] = self.ui.quit_confirmation.isChecked()
        self.tagger.window.update_toolbar_style()
        new_language = self.ui.ui_language.itemData(self.ui.ui_language.currentIndex())
        if new_language != config.setting["ui_language"]:
            config.setting["ui_language"] = self.ui.ui_language.itemData(self.ui.ui_language.currentIndex())
            dialog = QtGui.QMessageBox(
                QtGui.QMessageBox.Information,
                _('Language changed'),
                _('You have changed the interface language. You have to restart Picard in order for the change to take effect.'),
                QtGui.QMessageBox.Ok,
                self)
            dialog.exec_()
        config.setting["starting_directory"] = self.ui.starting_directory.isChecked()
        config.setting["starting_directory_path"] = os.path.normpath(unicode(self.ui.starting_directory_path.text()))
        self.update_layout_config()

    def restore_defaults(self):
        super(InterfaceOptionsPage, self).restore_defaults()
        self.update_buttons()

    def starting_directory_browse(self):
        item = self.ui.starting_directory_path
        path = QtGui.QFileDialog.getExistingDirectory(self, "", item.text())
        if path:
            path = os.path.normpath(unicode(path))
            item.setText(path)

    def _get_icon_from_name(self, name):
        return self.TOOLBAR_BUTTONS[name]['icon']

    def _insert_item(self, action, index=None):
        list_item = ToolbarListItem(action)
        list_item.setToolTip(_(u'Drag and Drop to re-order'))
        if action in self.TOOLBAR_BUTTONS:
            list_item.setText(_(self.TOOLBAR_BUTTONS[action]['label']))
            list_item.setIcon(icontheme.lookup(self._get_icon_from_name(action), icontheme.ICON_SIZE_MENU))
        else:
            list_item.setText(self.SEPARATOR)
        if index is not None:
            self.ui.toolbar_layout_list.insertItem(index, list_item)
        else:
            self.ui.toolbar_layout_list.addItem(list_item)
        return list_item

    def _all_list_items(self):
        return [self.ui.toolbar_layout_list.item(i).action_name
                for i in range(self.ui.toolbar_layout_list.count())]

    def _added_actions(self):
        actions = self._all_list_items()
        actions = filter(lambda x: x != 'separator', actions)
        return set(actions)

    def populate_action_list(self):
        self.ui.toolbar_layout_list.clear()
        for name in config.setting['toolbar_layout']:
            if name in self.ACTION_NAMES or name == 'separator':
                self._insert_item(name)

    def update_buttons(self):
        self.ui.add_button.setEnabled(self._added_actions() != self.ACTION_NAMES)
        current_row = self.ui.toolbar_layout_list.currentRow()
        self.ui.up_button.setEnabled(current_row > 0)
        self.ui.down_button.setEnabled(current_row < self.ui.toolbar_layout_list.count() - 1)

    def add_to_toolbar(self):
        display_list = set.difference(self.ACTION_NAMES, self._added_actions())
        selected_action, ok = AddActionDialog.get_selected_action(display_list, self)
        if ok:
            list_item = self._insert_item(selected_action, self.ui.toolbar_layout_list.currentRow() + 1)
            self.ui.toolbar_layout_list.setCurrentItem(list_item)
        self.update_buttons()

    def insert_separator(self):
        insert_index = self.ui.toolbar_layout_list.currentRow() + 1
        self._insert_item('separator', insert_index)

    def move_item(self, offset):
        current_index = self.ui.toolbar_layout_list.currentRow()
        offset_index = current_index - offset
        offset_item = self.ui.toolbar_layout_list.item(offset_index)
        if offset_item:
            current_item = self.ui.toolbar_layout_list.takeItem(current_index)
            self.ui.toolbar_layout_list.insertItem(offset_index, current_item)
            self.ui.toolbar_layout_list.setCurrentItem(current_item)
            self.update_buttons()

    def remove_action(self):
        item = self.ui.toolbar_layout_list.takeItem(self.ui.toolbar_layout_list.currentRow())
        del item
        self.update_buttons()

    def update_layout_config(self):
        config.setting['toolbar_layout'] = self._all_list_items()
        self._update_toolbar()

    def _update_toolbar(self):
        widget = self.parent()
        while not isinstance(widget, QtGui.QMainWindow):
            widget = widget.parent()
        # Call the main window's create toolbar method
        widget.create_action_toolbar()


class ToolbarListItem(QtGui.QListWidgetItem):
    def __init__(self, action_name, *args, **kwargs):
        super(ToolbarListItem, self).__init__(*args, **kwargs)
        self.action_name = action_name


class AddActionDialog(QtGui.QDialog):
    def __init__(self, action_list, *args, **kwargs):
        super(AddActionDialog, self).__init__(*args, **kwargs)

        layout = QtGui.QVBoxLayout(self)

        self.action_list = sorted([[_(self.parent().TOOLBAR_BUTTONS[action]['label']), action]
                                  for action in action_list])

        self.combo_box = QtGui.QComboBox(self)
        self.combo_box.addItems([label for label, action in self.action_list])
        layout.addWidget(self.combo_box)

        buttons = QtGui.QDialogButtonBox(
            QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def selected_action(self):
        return self.action_list[self.combo_box.currentIndex()][1]

    @staticmethod
    def get_selected_action(action_list, parent=None):
        dialog = AddActionDialog(action_list, parent)
        result = dialog.exec_()
        selected_action = dialog.selected_action()
        return (selected_action, result == QtGui.QDialog.Accepted)


register_options_page(InterfaceOptionsPage)
