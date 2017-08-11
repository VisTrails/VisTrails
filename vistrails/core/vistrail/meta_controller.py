import vistrails.core.db.io
from vistrails.core.vistrail.action import Action
from vistrails.core.vistrail.action_annotation import ActionAnnotation
from vistrails.core.vistrail.operation import ChangeOp, AddOp
from vistrails.core.vistrail.vistrail import MetaVistrail
from vistrails.core.vistrail.controller import VistrailController

class MetaVistrailController(VistrailController):
    def __init__(self, *args, **kwargs):
        VistrailController.__init__(self, *args, **kwargs)
        self.vt_controller = None

    def change_selected_version(self, new_version, report_all_errors=True,
                                do_validate=True, from_root=False):
        self.do_version_switch(new_version, report_all_errors,
                               do_validate, from_root)

    def do_version_switch(self, new_version, report_all_errors=False,
                          do_validate=True, from_root=False):
        """ do_version_switch(new_version: int,
                              resolve_all_errors: boolean) -> None
        Change the current vistrail version into new_version, reporting
        either the first error or all errors.

        """
        new_error = None
        self.current_vistrail = self.get_vistrail(new_version,
                                          # do_validate=do_validate,
                                          # from_root=from_root,
                                          # use_current=True
                                        )
        self.current_version = new_version
        self.vt_controller.update_vistrail(self.current_vistrail)

    def get_vistrail(self, version):
        return self.vistrail.getVistrail(version)

    def add_new_action(self, action, description=None, session=None):
        # create meta action that includes action using current meta version
        # as previd
        # need to create add op that has action embedded
        # action needs to reference current vistrail's prev id

        # keep the original vistrail intact in sub controller

        if action is not None:
            if self.current_version == -1:
                self.change_selected_version(MetaVistrail.ROOT_VERSION)

            meta_action = \
                vistrails.core.db.io.create_action([('add', action)], False)
            self.vistrail.add_action(meta_action, self.current_version,
                                     session)
            if description is not None:
                self.vistrail.change_description(description, meta_action.id)
            self.current_version = meta_action.db_id
            self.set_changed(True)
            self.recompute_terse_graph()
            return meta_action

    def prune_actions(self, action_list):
        if len(action_list) > 0:
            meta_action = vistrails.core.db.io.create_action(
                [('delete', action) for action in action_list])
            self.vistrail.add_action(meta_action, self.current_version,
                                     self.vt_controller.current_session)
            self.vistrail.change_description("Prune", meta_action.id)
            self.current_version = meta_action.db_id
            self.set_changed(True)
            self.recompute_terse_graph()
            self.invalidate_version_tree(False)
            return meta_action
        return None

    def set_tag(self, action_id, tag_str):
        if action_id is None:
            return None
        old_tag = self.vt_controller.vistrail.get_action_annotation(action_id,
                                                                    MetaVistrail.TAG_ANNOTATION)
        tag = ActionAnnotation(id=self.vistrail.idScope.getNewId(),
                               action_id=action_id,
                               key=MetaVistrail.TAG_ANNOTATION,
                               value=tag_str)
        desc = "Tag"
        if tag is None:
            meta_action = vistrails.core.db.io.create_action(
                [('delete', old_tag)])
            desc = "Delete Tag"
        elif old_tag is not None:
            meta_action = vistrails.core.db.io.create_action(
                [('change', old_tag, tag)])
            desc = "Change Tag"
        else:
            meta_action = vistrails.core.db.io.create_action(
                [('add', tag)])
            desc = "Add Tag"
        self.vistrail.add_action(meta_action, self.current_version,
                                 self.vt_controller.current_session)
        self.vistrail.change_description(desc, meta_action.id)

        self.current_version = meta_action.db_id
        self.set_changed(True)
        self.recompute_terse_graph()
        self.invalidate_version_tree(False)
        return meta_action

    def change_action(self, old_action, new_action, init_new_action=False):
        meta_action = vistrails.core.db.io.create_action(
            [('change', old_action, new_action)], False)
        self.vistrail.add_action(meta_action, self.current_version,
                                 self.vt_controller.current_session,
                                 init_inner=init_new_action)
        self.vistrail.change_description("Change Action", meta_action.id)

        self.current_version = meta_action.db_id
        self.set_changed(True)
        self.recompute_terse_graph()
        self.invalidate_version_tree(False)
        return meta_action

    def find_meta_impacts(self, meta_version_ids, action_ids):
        # need to build chains of actions (e.g. if one action changed to another
        # which then changed to the current meta id)
        # TODO for now, just get closest upstream / downstream
        for mv_id in meta_version_ids:
            if mv_id != MetaVistrail.ROOT_VERSION:
                meta_action = self.vistrail.actionMap[mv_id]
                for op in meta_action.operations:
                    if (op.vtType == 'change' and
                        op.what == 'action' and
                        op.new_obj_id in action_ids):
                        return mv_id
        return None

    def find_meta_links(self, action_id):
        # FIXME can be more efficient than processing each version id individually

        # care about any meta-action which changes one of these actions
        action_ids = set(self.vt_controller.vistrail.tree.path_to_root(action_id))

        # process path to root (reverse links)
        prev_meta = self.find_meta_impacts(
            self.vistrail.tree.path_to_root(self.current_version), action_ids)

        # process all children (forward links), sort by date
        child_dict = self.vistrail.tree.getVersionTree().bfs(self.current_version)
        children = list(sorted(child_dict.iterkeys(),
                               key=lambda v: self.vistrail.actionMap[v].date))
        next_meta = self.find_meta_impacts(children, action_ids)

        # for now, the action id remains the same (depends on how meta action
        # is set up)
        prev_t = (prev_meta, action_id) if prev_meta is not None else None
        next_t = (next_meta, action_id) if next_meta is not None else None
        return (prev_t, next_t)

    def update_function_meta(self, module, function_name, param_values, old_id=-1L,
                        aliases=[], query_methods=[], should_replace=True):
        # search up vistrail for last action that changed the function
        # may be just a single op in the action...would be better to be able to
        # change ops...instead of whole actions...
        vt = self.vt_controller.vistrail
        # update_function_ops uses a diff parameter order!
        ops = self.vt_controller.update_function_ops(module, function_name,
                                                     param_values, old_id,
                                                     should_replace, aliases,
                                                     query_methods)

        if not all(op[0] == 'change' for op in ops):
            # do normal action
            pass
        else:
            found = {}
            for op in ops:
                (action_id, op_id) = vt.find_action(self.vt_controller.current_version,
                                                    op[1].vtType, op[1].real_id,
                                                    *op[3:])
                if op_id is not None:
                    if action_id not in found:
                        found[action_id] = {}
                    found[action_id][op_id] = op
                else:
                    print "OP NOT FOUND!", op
            for (action_id, op_dict) in found.iteritems():
                old_action = vt.actionMap[action_id]
                # print "REPLACING ACTION:", old_action
                new_ops = []
                for old_op in old_action.operations:
                    if old_op.id in op_dict:
                        op = op_dict[old_op.id]
                        # do replace
                        assert old_op.db_data.vtType == 'parameter'
                        old_param = old_op.db_data
                        new_param = op[2]
                        if old_op.vtType == 'add':
                            new_op = AddOp(id=old_op.id,
                                           pos=old_op.pos,
                                           what=old_op.what,
                                           objectId=new_param.real_id,
                                           parentObjId=old_op.parentObjId,
                                           parentObjType=old_op.parentObjType,
                                           data=new_param)
                        else:
                            new_op = ChangeOp(id=old_op.id,
                                              pos=old_op.pos,
                                              what=old_op.what,
                                              oldObjId=old_op.old_obj_id,
                                              newObjId=new_param.real_id,
                                              parentObjId=old_op.parentObjId,
                                              parentObjType=old_op.parentObjType,
                                              data=new_param)
                        new_ops.append(new_op)
                    else:
                        new_ops.append(old_op)
                new_action = Action(id=old_action.id,
                                    prevId=old_action.parent,
                                    operations=new_ops)
                # print "NEW ACTION:", new_action
                # for op in new_action.operations:
                #     print "  NEW OP:", op
                self.change_action(old_action, new_action, init_new_action=True)