import re
import StringIO

from core.modules.vistrails_module import Module
from core.modules.module_registry import get_module_registry

from extras.core.java_vm import get_java_vm, build_jarray


_JAVA_VM = get_java_vm()

Evaluation = _JAVA_VM.weka.classifiers.Evaluation

JavaString = _JAVA_VM.java.lang.String
Class = _JAVA_VM.java.lang.Class


def _direct(param):
    return param
def _file(param):
    return param.name


class EvaluateClassifier(Module):
    """Wrapper for the EvaluateClassifier class.

    Because EvaluateClassifier is meant to be used from the commandline, it
    accepts an array of string options, which is really inconvenient for
    programmatical use.
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

    def compute(self):
        classifier = self.getInputFromPort('classifier')
        options = []
        for portname, description, option, sig, convert in \
                EvaluateClassifier.OPTIONS:
            if self.hasInputFromPort(portname):
                value = self.getInputFromPort(portname)
                if value is not None:
                    options.extend([option, convert(value)])

        options = build_jarray(JavaString, options)

        stdout = Evaluation.evaluateModel(classifier, options)

        self.setResult('stdout', stdout)


class EvaluationStatistics(Module):
    """Parses the output of the EvaluateClassifier module.

    Because EvaluateClassifier is meant to be used from the commandline, it
    outputs human-readable details on the evaluation. This module parses it
    into a more useful format, that can be passed to EvaluationResultTable for
    instance.
    """
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

    def compute(self):
        stdout = self.getInputFromPort('stdout')

        results = dict()

        reader = StringIO.StringIO(stdout)

        classifier_name = reader.readline()
        self.setResult('classifier_name', classifier_name)
        results['classifier_name'] = classifier_name

        pos = stdout.find('=== Stratified cross-validation ===')
        reader.seek(pos)
        for n, line in enumerate(reader):
            if n > 1 and (not line or line.startswith('===')):
                break

            m = EvaluationStatistics._line_format.match(line)
            if m:
                try:
                    key = EvaluationStatistics.FIELDS[m.group(1)]
                except KeyError:
                    continue
                res = float(m.group(2))
                self.setResult(key, res)
                results[key] = res

        self.setResult('results', results)


# TODO : EvaluationResultTable module


def register_additional_modules():
    reg = get_module_registry()


    reg.add_module(EvaluateClassifier)
    reg.add_input_port(
            EvaluateClassifier, 'classifier',
            '(edu.utah.sci.vistrails.weka:Classifier:weka|classifiers)')

    for portname, description, option, sig, convert in \
            EvaluateClassifier.OPTIONS:
        reg.add_input_port(
                EvaluateClassifier, portname,
                sig)

    reg.add_output_port(
            EvaluateClassifier, 'stdout',
            '(edu.utah.sci.vistrails.basic:String)')


    reg.add_module(EvaluationStatistics)
    reg.add_input_port(
            EvaluationStatistics, 'stdout',
            '(edu.utah.sci.vistrails.basic:String)')
    reg.add_output_port(
            EvaluationStatistics, 'results',
            '(edu.utah.sci.vistrails.basic:Dictionary)')
    reg.add_output_port(
            EvaluationStatistics, 'classifier_name',
            '(edu.utah.sci.vistrails.basic:String)')

    for string, portname in EvaluationStatistics.FIELDS.iteritems():
        reg.add_output_port(
                EvaluationStatistics, portname,
                '(edu.utah.sci.vistrails.basic:Float)')
