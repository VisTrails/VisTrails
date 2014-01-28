VisTrails Java Spreadsheet
==========================

This package was originally written for the Java (Jython) version of VisTrails,
which was a complete rewrite of the graphical interface with Swing.

It can now be run in the standard Python/Qt version through JPype (as it is
pure Java).


Why this package
----------------

The Qt spreadsheet cannot contain Java visualizations at the moment. To work
around that, we have a different Swing-based spreadsheet window, in which AWT
or Swing components can be displayed.


How it works
------------

The Java Spreadsheet is written in Java instead of Python to work around
limitations of Python-Java bridge extensions. This means that a JAR file
containing the compiled class files must be built from the Java source for it
to be runnable.


Building javaspreadsheet.jar
----------------------------

The JAR must be placed in a directory where VisTrails will look for it (for
instance, javalibs/ in the main application directory).

The Java sources, along with an Eclipse project and a Makefile, are located in
vistrails/packages/javaspreadsheet/java.


### Building with Eclipse

An Eclipse project is included with the sources. You can use the JAR
description file 'javaspreadsheet.jardesc' to easily create the JAR file from
Eclipse (or just create a JAR with all the .class files).


### Building with the Makefile

You will need a JDK. The 'javac' executable must either be in your PATH or in
$JAVA_HOME/bin (you can alter the Makefile to match your system's
configuration if necessary). Simply running 'make' from the java sources
directory should work in most cases.


Example
-------

An example of usage of a Java library (Weka) is available:
[form_classification](http://dl.dropboxusercontent.com/u/13131521/20120627-weka-form_classification/l.html).
