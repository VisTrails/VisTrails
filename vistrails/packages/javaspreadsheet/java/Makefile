# Java tools
# We try to use the JAVA_HOME environment variable, or assume that the tools
# are in the path if undefined
# JAVA_HOME needs to point to a JDK, not a JRE!
ifdef JAVA_HOME
	JAVAC = "$(JAVA_HOME)"/bin/javac
	JAR = "$(JAVA_HOME)"/bin/jar
else
	JAVAC = javac
	JAR = jar
endif

# Sources location
SOURCES = src

# Where to put the class files
BIN = bin

# Where to put the generated JAR file
OUTPUT_JAR = ../../../../javalibs/javaspreadsheet.jar

# The sources
INPUT = \
 edu/utah/sci/vistrails/javaspreadsheet/Cell.java \
 edu/utah/sci/vistrails/javaspreadsheet/CellInfos.java \
 edu/utah/sci/vistrails/javaspreadsheet/CellLocation.java \
 edu/utah/sci/vistrails/javaspreadsheet/CellManipulator.java \
 edu/utah/sci/vistrails/javaspreadsheet/Sheet.java \
 edu/utah/sci/vistrails/javaspreadsheet/SheetReference.java \
 edu/utah/sci/vistrails/javaspreadsheet/Spreadsheet.java \
 edu/utah/sci/vistrails/javaspreadsheet/SpreadsheetInterface.java \
 edu/utah/sci/vistrails/javaspreadsheet/SpreadsheetModel.java \
 edu/utah/sci/vistrails/javaspreadsheet/SpreadsheetTable.java \
 edu/utah/sci/vistrails/javaspreadsheet/rowheader/JTableRowHeader.java \
 edu/utah/sci/vistrails/javaspreadsheet/rowheader/TableRowResizer.java


.PHONY: all build

all: $(OUTPUT_JAR)

$(OUTPUT_JAR): build
	$(JAR) cf $@ -C $(BIN) .

# Because javac behaves in an odd manner anyway, we don't even try to use
# make's dependency tracking to figure out what needs to be rebuilt
build: $(patsubst %,$(SOURCES)/%,$(INPUT))
	mkdir $(BIN)
	$(JAVAC) -d $(BIN) -sourcepath $(SOURCES) $^
