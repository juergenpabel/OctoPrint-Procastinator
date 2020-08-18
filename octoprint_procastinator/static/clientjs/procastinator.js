(function (global, factory) {
    if (typeof define === "function" && define.amd) {
        define(["OctoPrintClient"], factory);
    } else {
        factory(global.OctoPrintClient);
    }
})(this, function(OctoPrintClient) {
    var OctoPrintProcastinatorClient = function(base) {
        this.base = base;
    };

    OctoPrintProcastinatorClient.prototype.get = function(refresh, opts) {
        return this.base.get(this.base.getSimpleApiUrl("procastinator"), opts);
    };

    OctoPrintProcastinatorClient.prototype.select = function(choice, opts) {
        var data = {
            choice: choice
        };
        return this.base.simpleApiCommand("procastinator", "select", data, opts);
    };

    OctoPrintClient.registerPluginComponent("procastinator", OctoPrintProcastinatorClient);
    return OctoPrintProcastinatorClient;
});
