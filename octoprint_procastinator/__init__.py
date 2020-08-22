# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

__license__ = 'GNU Affero General Public License http://www.gnu.org/licenses/agpl.html'
__copyright__ = "Copyright (C) 2018 The OctoPrint Project - Released under terms of the AGPLv3 License"

from datetime import datetime,time

import octoprint.plugin
from octoprint.events import Events
from octoprint.util   import ResettableTimer

import flask
from flask_babel import gettext


class ProcastinatorPlugin(octoprint.plugin.AssetPlugin,
                                octoprint.plugin.EventHandlerPlugin,
                                octoprint.plugin.SettingsPlugin,
                                octoprint.plugin.SimpleApiPlugin,
                                octoprint.plugin.TemplatePlugin):

	# noinspection PyMissingConstructor
	def __init__(self):
		self._procastinating = False
		self._worktimes = list()


	def initialize(self):
		self._procastinating = False
		self._worktimes = list()


	def get_assets(self):
		return dict(js=["js/procastinator.js"],
		            clientjs=["clientjs/procastinator.js"])


	def get_update_information(*args, **kwargs):
		return dict(
		    procastinator=dict(
		        displayName=_plugin_name,
		        displayVersion=self._plugin_version,

		        type="github_release",
		        user="juergenpabel",
		        repo="OctoPrint-Procastinator",
		        current=self._plugin_version,

		        pip="https://github.com/juergenpabel/OctoPrint-Procastinator/archive/{target_version}.zip"
		    )
		)


	#~ EventHandlerPlugin
	def on_event(self, event, payload):
		if event == Events.PRINT_STARTED:
			if self._settings.get_boolean(["enabled"]):
				now = datetime.strptime(datetime.now().strftime("%H:%M:%S"), "%H:%M:%S")
				start = datetime.strptime(self._settings.get(["starttime"])+":00", "%H:%M:%S")
				end = datetime.strptime(self._settings.get(["endtime"])+":00", "%H:%M:%S")
				if (start < end and (now >= start and now <= end)) or (start > end and (now > start or now < end)):
					self._procastinating = True
					self._printer.set_job_on_hold(True)
					self._worktimes = list()
					self._worktimes.append("NOW")
					for worktime in self._settings.get(["worktimes"]):
						if worktime['time'] is not None:
							self._worktimes.append(worktime['time'])
					self._plugin_manager.send_plugin_message(self._identifier, dict(action="dialog:show", template="dialog:choice", parameters=self._worktimes))
		if event == Events.PRINT_DONE:
			self._procastinating = False
			self._plugin_manager.send_plugin_message(self._identifier, dict(action="notice:close"))
		if event == Events.DISCONNECTED:
			self._procastinating = False
			self._plugin_manager.send_plugin_message(self._identifier, dict(action="dialog:close"))
			self._plugin_manager.send_plugin_message(self._identifier, dict(action="notice:close"))
		pass


	#~ SettingsPlugin
	def get_settings_defaults(self):
		return dict(enabled=False,starttime="00:00",endtime="23:59",worktimes=list(({'time': None},{'time': None},{'time': None},{'time': None},{'time': None})))

	#~ SimpleApiPlugin
	def get_api_commands(self):
		return dict(select=["choice"])

	
	def on_timedout(self):
		self._procastinating = False
		self._printer.set_job_on_hold(False)
		self._plugin_manager.send_plugin_message(self._identifier, dict(action="dialog:close"))
		self._plugin_manager.send_plugin_message(self._identifier, dict(action="notice:show", template="notice:continue"))


	def on_api_command(self, command, data):
		if command == "select":
			if self._procastinating is not True:
				return

			self._plugin_manager.send_plugin_message(self._identifier, dict(action="dialog:close"))
			choice = data["choice"]
			if choice == "NOW":
				self._procastinating = False
				self._printer.set_job_on_hold(False)
			else:
				try:
					now = datetime.strptime(datetime.now().strftime("%H:%M:%S"), "%H:%M:%S")
					work = datetime.strptime(choice+":00", "%H:%M:%S")
					delay = (work - now).seconds
					if delay < 0:
						delay += 86400
					self._logger.info("Procastinating for {0} seconds".format(delay))
					self.timer = ResettableTimer(delay, self.on_timedout) #, (self, ))
					self.timer.start()
					self._plugin_manager.send_plugin_message(self._identifier, dict(action="notice:show", template="notice:until", parameters=choice))
				except ValueError:
					self._logger.error("on_api_command() invoked with invalid choice='{0}'".format(choice))
					self._printer.set_job_on_hold(False)
					self._procastinating = False


	def on_api_get(self, request):
		if self._procastinating is not True:
			return flask.jsonify()
		else:
			return flask.jsonify(action="dialog:show", template="dialog:choice", parameters=self._worktimes)


	#~ TemplatePlugin
	def get_template_configs(self):
		return [dict(type="settings", name=gettext("Procastinator"), custom_bindings=False)]



__plugin_name__ = "Procastinator"
__plugin_description__ = "Allows your printer to procastinate on print jobs"
__plugin_author__ = "Jürgen Pabel"
__plugin_license__ = "AGPLv3"
__plugin_pythoncompat__ = ">=2.7,<4"
__plugin_implementation__ = ProcastinatorPlugin()
__plugin_hooks__ = {
                      "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
                   }
