import re
import StringIO

from vistrails.core.modules.vistrails_module import Module
from vistrails.core.modules.module_registry import get_module_registry

from vistrails.packages.java.java_vm import get_java_vm, build_jarray
from vistrails.packages.tabledata.common import TableObject


_JAVA_VM = get_java_vm()


Evaluation = _JAVA_VM.weka.classifiers.Evaluation

JavaString = _JAVA_VM.java.lang.String
Class = _JAVA_VM.java.lang.Class


reg = get_module_registry()

Classifier = reg.get_module_by_name('Java#weka',
                                    'Classifier',
                                    'weka|classifiers')


def _direct(param):
    return param
def _file(param):
    return param.name


class EvaluateClassifier(Module):
    """Wrapper for the EvaluateClassifier class.

    Because EvaluateClassifier is meant to be used from the commandline, it
    accepts an array of string options, which is really inconvenient for
    programmatical use.
    This module also parses the human-readable output of the class into a more
    useful format, that can be passed to EvaluationResultTable for instance.
    """
    OPTIONS = [
            ('training-file', "File with the training data",
             '-t', '(edu.utah.sci.vistrails.basic:File)', _file), # req
            ('test-file', "File with the test data",
             '-T', '(edu.utah.sci.vistrails.basic:File)', _file),
            ('class-index', "Index of the class attribute",
             '-c', '(edu.utah.sci.vistrails.basic:Integer)', _direct),
            ('folds', "The number of folds for the cross-validation",
             '-x', '(edu.utah.sci.vistrails.basic:Integer)', _direct),
            ('split-percentage', "Train/test set split in percent",
             '-split-percentage', '(edu.utah.sci.vistrails.basic:Integer)',
             _direct),
            ('cost-matrix', "File containing the cost matrix",
             '-m', '(edu.utah.sci.vistrails.basic:File)', _file),
            ('classifier-load-file', "Load classifier from the given file",
             '-l', '(edu.utah.sci.vistrails.basic:File)', _file),
            ('classifier-save-file', "Save classifier to the given file",
             '-d', '(edu.utah.sci.vistrails.basic:File)', _file),
            ('xml-options', "Read the options from this XML file",
             '-xml', '(edu.utah.sci.vistrails.basic:File)', _file)]

    _line_format = re.compile(
            r'^((?:[A-Za-z]| (?! ))+)  .+ ([0-9.]+)(?: *%)? *$')
    FIELDS = {
            "Correctly Classified Instances": 'correct_rate',
            "Incorrectly Classified Instances": 'error_rate',
            "Kappa statistic": 'kappa_statistic',
            "Mean absolute error": 'mean_abs_error',
            "Root mean squared error": 'root_mean_sq_error',
            "Relative absolute error": 'rel_abs_error',
            "Root relative squared error": 'root_rel_sq_error',
            "Total Number of Instances": 'instances'}

    _input_ports = [
            ('classifier', Classifier)] + [
            (name, sig)
            for name, description, option, sig, convert in OPTIONS]
    _output_ports = [
            ('stdout', '(edu.utah.sci.vistrails.basic:String)'),
            ('results', '(edu.utah.sci.vistrails.basic:Dictionary)'),
            ('classifier_name', '(edu.utah.sci.vistrails.basic:String)')] + [
            (name, '(edu.utah.sci.vistrails.basic:Float)')
            for name in FIELDS.itervalues()]

    def compute(self):
        classifier = self.get_input('classifier')
        options = []
        for portname, description, option, sig, convert in \
                EvaluateClassifier.OPTIONS:
            if self.has_input(portname):
                value = self.get_input(portname)
                if value is not None:
                    options.extend([option, convert(value)])

        options = build_jarray(JavaString, options)

        stdout = Evaluation.evaluateModel(classifier, options)

        self.set_output('stdout', stdout)

        results = dict()

        reader = StringIO.StringIO(stdout)

        classifier_name = ''
        while not classifier_name:
            classifier_name = reader.readline().strip()
        if classifier_name.startswith('=='):
            classifier_name = ''

        self.set_output('classifier_name', classifier_name)
        results['classifier_name'] = classifier_name

        pos = stdout.find('=== Stratified cross-validation ===')
        reader.seek(pos)
        for n, line in enumerate(reader):
            if n > 1 and (not line or line.startswith('===')):
                break

            m = EvaluateClassifier._line_format.match(line)
            if m:
                try:
                    key = EvaluateClassifier.FIELDS[m.group(1)]
                except KeyError:
                    continue
                res = float(m.group(2))
                self.set_output(key, res)
                results[key] = res

        self.set_output('results', results)


class EvaluationResultTable(Module):
    """Displays the results of EvaluateClassifier as an HTML table.

    This module can be used to turn the output of the EvaluateClassifier
    module into an HTML table suitable for display.
    """
    _input_ports = [
            ('statistics', '(edu.utah.sci.vistrails.basic:Dictionary)')]
    _output_ports = [
            ('table', '(org.vistrails.vistrails.tabledata:Table)')]

    FIELDS = ['classifier_name', 'correct_rate', 'error_rate',
              'kappa_statistic', 'mean_abs_error', 'root_mean_sq_error',
              'rel_abs_error', 'root_rel_sq_error']

    def compute(self):
        statistics = self.get_input_list('statistics')
        self.set_output('table',
                        TableObject.from_dicts(statistics, self.FIELDS))


_modules = [EvaluateClassifier, EvaluationResultTable]
