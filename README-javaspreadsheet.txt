This README file concerns the 'javaspreadsheet' package, that was originally
written for the Java (Jython) version of VisTrails, but can also be run in the
standard Python/Qt version through JPype (as it is pure Java).


# Introduction

The Java Spreadsheet has been rewritten in Java instead of Python to avoid
some issues with JPype. This means that a JAR file containing the compiled
class files need to be built, else the VisTrails package will not work.


# Building javaspreadsheet.jar

The JAR must be placed in a directory where VisTrails will look for it (for
instance, javalibs/ in the main application directory).

The Java sources, along with an Eclipse project and a Makefile, are located in
vistrails/packages/javaspreadsheet/java.


## Building with Eclipse

An Eclipse project is included with the sources. You can use the JAR
description file 'javaspreadsheet.jardesc' to easily create the JAR file from
Eclipse (or just create a JAR with all the .class files).


## Building with the Makefile

You will need a JDK. The 'javac' executable must either be in your PATH or in
$JAVA_HOME/bin (you can alter the Makefile to match your system's
configuration if necessary). Simply running 'make' from the java sources
directory should work in most cases.
