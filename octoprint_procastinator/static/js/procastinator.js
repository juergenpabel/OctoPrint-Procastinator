$(function() {
    function ProcastinatorViewModel(parameters) {
        var self = this;
        self.settings = parameters[0];

        self.dialog = ko.observable(undefined);
        self.dialog_parameters = ko.observableArray([]);

        self.notice = ko.observable(undefined);

        self.requestData = function() {
            OctoPrint.plugins.procastinator.get().done(self.fromResponse);
        };


        self.fromResponse = function(data) {
            if (data.hasOwnProperty("action")) {
                switch( data.action ) {
                    case "dialog:show": {
                        if (data.hasOwnProperty("template") && data.hasOwnProperty("parameters")) {
                            self.dialog_parameters(data.parameters);
                            self.showDialog(self.getTemplate(data.template), data.parameters);
                        }
                        break;
                    }
                    case "dialog:close": {
                        self.dialog_parameters([]);
                        self._closeDialog();
                        break;
                    }
                    case "notice:show": {
                        if (data.hasOwnProperty("template") ) {
                            self.showNotice(self.getTemplate(data.template), []);
                        }
                        break;
                    }
                    case "notice:close": {
                        break;
                    }
                }
            }
        };


        self.getTemplate = function(id) {
            switch( id ) {
                case "dialog:choice": {
                    return gettext("Please select when start/continue the current print job:");
                }
                case "notice:until": {
                    return gettext("Waiting until XX:XX before starting/continuing the current print job.");
                }
                case "notice:continue": {
                    return gettext("Starting/Continuing the current print job.");
                }
            }
            return "BUG: unknown template";
        };


        self.showNotice = function(notice_text, notice_parameter) {
            if (self.notice() !== undefined) {
                self.notice().remove();
            }
            message = notice_text.replace("XX:XX", notice_parameter);
            self.notice(new PNotify({
                                     title: gettext("Procastinator"),
                                     text: message,
                                     hide: false,
                                     icon: "fa fa-bell-o",
                                     buttons: {
                                         sticker: false,
                                         closer: true
                                     }
                         }));
	}


        self.showDialog = function(dialog_text, dialog_parameters) {
            var dialog_choices = Array.from(dialog_parameters);
            dialog_choices[0] = gettext("NOW");

            var opts = {
                title: gettext("Procastinator"),
                message: dialog_text,
                selections: dialog_choices,
                maycancel: true, // see #3171
                onselect: function(index) {
                    if (index > -1) {
                        self._select(index);
                    }
                },
                onclose: function() {
        	    self.dialog = ko.observable(undefined);
                }
            };
            self.dialog(showSelectionDialog(opts));
        };


        self._select = function(index) {
            OctoPrint.plugins.procastinator.select(self.dialog_parameters()[index]);
        };


        self._closeDialog = function() {
            if (self.dialog() !== undefined) {
                self.dialog('hide');
        	self.dialog = ko.observable(undefined);
            }
        };


        self.onStartupComplete = function() {
            self.requestData();
        };


        self.onDataUpdaterPluginMessage = function(plugin, data) {
            if (plugin !== "procastinator") {
                return;
            }

            switch (data.action) {
                case "notice:show": {
                    self.showNotice(self.getTemplate(data.template), data.parameters);
                    break;
                }
                case "notice:close": {
		    if (self.notice() !== undefined) {
                         self.notice().remove();
                    }
                    break;
                }
                case "dialog:show": {
                    self.dialog_parameters(data.parameters);
                    self.showDialog(self.getTemplate(data.template), data.parameters);
                    break;
                }
                case "dialog:close": {
                    self.dialog_parameters([]);
                    self._closeDialog();
                    break;
                }
            }
        }

    }

    OCTOPRINT_VIEWMODELS.push({
        construct: ProcastinatorViewModel,
        dependencies: ["settingsViewModel"],
        elements: []
    });
});
