from core.modules.vistrails_module import Module
from core.modules.module_registry import get_module_registry

from java.lang import String as JavaString, Class
import jarray

from weka.classifiers import Evaluation


def _direct(param):
    return param
def _file(param):
    return param.name


EVALUATION_OPTIONS = [
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


class EvaluateClassifier(Module):
    def compute(self):
        classifier = self.getInputFromPort('classifier')
        options = []
        for portname, description, option, sig, convert in EVALUATION_OPTIONS:
            if self.hasInputFromPort(portname):
                value = self.getInputFromPort(portname)
                if value is not None:
                    options.extend([option, convert(value)])

        options = jarray.array(options, JavaString)

        stdout = Evaluation.evaluateModel(classifier, options)

        self.setResult('stdout', stdout)


def register_additional_modules():
    reg = get_module_registry()

    reg.add_module(EvaluateClassifier)
    reg.add_input_port(
            EvaluateClassifier, 'classifier',
            '(edu.utah.sci.vistrails.weka:Classifier:weka|classifiers)')

    for portname, description, option, sig, convert in EVALUATION_OPTIONS:
        reg.add_input_port(
                EvaluateClassifier, portname,
                sig)

    reg.add_output_port(
            EvaluateClassifier, 'stdout',
            '(edu.utah.sci.vistrails.basic:String)')
