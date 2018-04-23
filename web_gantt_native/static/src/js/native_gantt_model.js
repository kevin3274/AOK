odoo.define('web_gantt_native.NativeGanttModel', function (require) {
"use strict";

var AbstractModel = require('web.AbstractModel');
var GanttToolField = require('web_gantt_native.ToolField');
var GanttTimeLineGhost = require('web_gantt_native.Ghost');
var GanttTimeLineFirst = require('web_gantt_native.BarFirst');

return AbstractModel.extend({

    init: function () {
        this._super.apply(this, arguments);
        this.gantt = null;

    },

    get: function () {
        return _.extend({}, this.gantt);
    },

    load: function (params) {
        this.modelName = params.modelName;
        this.fields_view  = params.fieldsView;
        this.gantt = {
            modelName : params.modelName,
            group_bys : params.groupedBy,
            domains : params.domain || [],
            contexts :  params.context || {},
            fields_view : params.fieldsView,
            fields : params.fields,
        }

        return this._do_load();

    },




        //---1---//
    _do_load: function () {




        var domains = this.gantt.domains;
        var contexts = this.gantt.contexts;
        var group_bys = this.gantt.group_bys;

        var self = this;

        self.main_group_id_name = self.fields_view.arch.attrs.main_group_id_name;

        // Sort allow only if Group by project and domain search by project.
        // Project get from XML = main_group_id_name = "project_id"

        self.ItemsSorted = false;
        if (group_bys.length === 1){

            if (group_bys[0] === self.main_group_id_name){
                 self.ItemsSorted = true;
            }
            if (domains.length > 0){
                if (domains[0][0] !== self.main_group_id_name){
                 self.ItemsSorted = false;
                }
            }

            if (domains.length > 1){
                self.ItemsSorted = false;
            }
        }

        if (self.fields_view.arch.attrs.no_group_sort_mode){
            self.ItemsSorted = false;
        }



        self.last_domains = domains;
        self.last_contexts = contexts;
        self.last_group_bys = group_bys;
        self.date_start = null;
        self.date_stop = null;

        var n_group_bys = [];

        // select the group by - we can select group by from attribute where XML if not determinate dafault group
        // for model

        if (this.fields_view.arch.attrs.default_group_by) {
           n_group_bys = this.fields_view.arch.attrs.default_group_by.split(',');
        }

        if (group_bys.length) {
            n_group_bys = group_bys;
        }


        var getFields = GanttToolField.getFields(self, group_bys);
        self.model_fields = getFields["model_fields"];
        self.model_fields_dict = getFields["model_fields_dict"];

        var fields = self.model_fields;
        fields.push('display_name');

        // this.fields_view.arch.attrs.default_group_by
        var export_wizard = false;

        if (self.fields_view.arch.attrs.hasOwnProperty('export_wizard')){
            export_wizard = self.fields_view.arch.attrs.export_wizard
        }

        self.gantt.data = {
            ItemsSorted : self.ItemsSorted,
            ExportWizard : export_wizard,
            model_fields : fields,
            model_fields_dict : self.model_fields_dict,
            model_fields_view : self.fields_view
        };


        return this._rpc({
                model: this.modelName,
                method: 'search_read',
                context: this.gantt.contexts,
                domain: this.gantt.domains,
                fields: _.uniq(fields),
            })
            .then(function (data) {
                return self.on_data_loaded_dummy(data, n_group_bys);
            });

    },


    on_data_loaded_dummy: function(tasks, group_bys) {
        var self = this;
        return self.on_data_loaded_predecessor(tasks, group_bys);
    },


        //Fist Entry poin load predecessor after. get atributes from XML
    on_data_loaded_predecessor: function(tasks, group_bys) {
        var self = this;
        var ids = _.pluck(tasks, "id");

        var predecessor_model = self.fields_view.arch.attrs.predecessor_model;
        var predecessor_task_id = self.fields_view.arch.attrs.predecessor_task_id;
        var predecessor_parent_task_id = self.fields_view.arch.attrs.predecessor_parent_task_id;
        var predecessor_type = self.fields_view.arch.attrs.predecessor_type;

        if (predecessor_model) {

            return this._rpc({
                    model: predecessor_model,
                    method: 'search_read',
                    context: this.gantt.contexts,
                    domain: [[predecessor_task_id, 'in', _.uniq(ids)]],
                    fields: _.uniq([predecessor_task_id, predecessor_parent_task_id, predecessor_type])
                })
                .then(function (result) {
                    self.gantt.data.predecessor = result;
                    return self.on_data_loaded_ghost(tasks, group_bys);
                });
            }
        else{
            return self.on_data_loaded_ghost(tasks, group_bys);
        }

    },

            //Fist Entry poin load predecessor after. get atributes from XML
    on_data_loaded_ghost: function(tasks, group_bys) {
        var self = this;
        var ids = _.pluck(tasks, "id");

        var ghost_id = self.fields_view.arch.attrs.ghost_id;
        var ghost_model = self.fields_view.arch.attrs.ghost_model;
        var ghost_name = self.fields_view.arch.attrs.ghost_name;
        var ghost_date_start = self.fields_view.arch.attrs.ghost_date_start;
        var ghost_date_end = self.fields_view.arch.attrs.ghost_date_end;
        var ghost_durations = self.fields_view.arch.attrs.ghost_durations;

        if (ghost_model) {
            return this._rpc({
                    model: ghost_model,
                    method: 'search_read',
                    context: this.gantt.contexts,
                    domain: [[ghost_id, 'in', _.uniq(ids)]],
                    fields: _.uniq([ghost_id ,ghost_name, ghost_date_start, ghost_date_end, ghost_durations])
                })
                .then(function (result) {
                    self.gantt.data.Ghost = result;
                    self.gantt.data.Ghost_Data = GanttTimeLineGhost.get_data_ghosts(self);

                    return self.on_data_loaded_barfirst(tasks, group_bys);
                });

        }
        else{
            return self.on_data_loaded_barfirst(tasks, group_bys);
        }

    },

    on_data_loaded_barfirst: function(tasks, group_bys) {

        var self = this;

        if (self.ItemsSorted) {

            var barfirst_field = "project_id";

            var barfirst_field_ids = _.pluck(tasks, "project_id");

            var ids = _.pluck(barfirst_field_ids, "0");

            var barfirst_model = "project.project";
            var barfirst_name = "name";
            var barfirst_date_start = "date_start";
            var barfirst_date_end = "date_end";


            return this._rpc({
                    model: barfirst_model,
                    method: 'search_read',
                    context: this.gantt.contexts,
                    domain: [['id', 'in', _.uniq(ids)]],
                    fields: _.uniq(['id', barfirst_name, barfirst_date_start, barfirst_date_end])
                })
                .then(function (result) {
                    self.gantt.data.BarFirst = result;
                    self.gantt.data.BarFirst_Data = GanttTimeLineFirst.get_data_barfirst(self);

                    return self.on_data_loaded_name_get(tasks, group_bys);
                });

        }
        else{
            return self.on_data_loaded_name_get(tasks, group_bys);
        }

    },


        //Get name get from model form name field
    on_data_loaded_name_get: function(tasks, group_bys) {
        var self = this;
        var ids = _.pluck(tasks, "id");

        return this._rpc({
                model: this.modelName,
                method: 'name_get',
                args: [ids],
                context: this.gantt.contexts,
            })
            .then(function (names) {
                var ntasks = _.map(tasks, function(task) {
                        return _.extend({__name: _.detect(names, function(name) { return name[0] == task.id; })[1]}, task);
                });

                // return self.gantt_render(ntasks, group_bys);
                self.gantt.data.ntasks = ntasks;
                self.gantt.data.group_bys = group_bys;

                var rrt = 67;
            });


    },







    reload: function (handle, params) {
        if (params.domain) {
            this.gantt.domains = params.domain;
        }
        if (params.context) {
            this.gantt.contexts = params.context;
        }
        if (params.groupBy) {
            this.gantt.group_bys = params.groupBy;
        }
        return this._do_load();
    },

});

});
