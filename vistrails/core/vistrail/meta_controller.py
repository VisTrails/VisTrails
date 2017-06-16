from vistrails.core.vistrail.controller import VistrailController

class MetaVistrailController(VistrailController):
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
        self.vistrail = self.get_vistrail(new_version,
                                          # do_validate=do_validate,
                                          # from_root=from_root,
                                          # use_current=True
                                        )
        self.current_version = new_version

    def get_vistrail(self, version):
        return self.vistrail.getVistrail(version)
