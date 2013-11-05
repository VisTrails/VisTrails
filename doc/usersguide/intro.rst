******************
What Is VisTrails?
******************

VisTrails is a new system that provides data and process management
support for exploratory computational tasks. It combines features of
both workflow and visualization systems. Similar to workflow systems, it allows the combination of loosely-coupled resources, specialized
libraries, and grid and Web services. Similar to some
visualization systems, it provides a mechanism for parameter
exploration and comparison of different results. But unlike these other systems,
VisTrails was designed to manage *exploratory processes* in which
computational tasks evolve over time as a user iteratively
formulates and tests hypotheses. A key distinguishing
feature of VisTrails is its comprehensive provenance infrastructure that
maintains detailed history information about the steps followed in the
course of an exploratory task. VisTrails leverages this information to
provide novel operations and user interfaces that streamline this
process.

Important Features
""""""""""""""""""
One of our main uses for VisTrails has been exploratory visualization,
but the system is much more general and provides many other features,
such as:

* *Flexible Provenance Architecture.* VisTrails transparently
  tracks changes made to workflows, including all the steps followed in the
  exploration. The system can optionally track run-time information
  about the execution of workflows (|eg| who executed a module, on
  which machine, elapsed time |etc|). |vistrails| also provides a
  flexible annotation framework whereby you can specify
  application-specific provenance information.

* *Querying and Re-using History.*  The provenance
  information is stored in a structured way. You have a choice of
  using a relational database (such as MySQL or IBM DB2) or XML files in
  the file system. The system provides flexible and intuitive query
  interfaces through which you can explore and reuse provenance
  information.  You can formulate simple keyword-based and selection
  queries (|eg| find a visualization created by a given user) as well
  as structured queries (|eg| find visualizations that apply
  simplification before an isosurface computation for irregular grid
  data sets).

* *Support for collaborative exploration.*  The system can be
  configured with a database backend that can be used as a shared
  repository.  It also provides a synchronization facility that allows
  multiple users to collaborate asynchronously and in a disconnected
  fashion---you can check in and check out changes, akin to a
  version control system (|eg| SVN: http://subversion.tigris.org).

* *Extensibility.* |vistrails| provides a very simple plugin
  functionality that can be used to dynamically add packages and
  libraries. Neither changes to the user interface nor re-compilation
  of the system are necessary.  Because |vistrails| is written in
  Python, the integration of Python-wrapped libraries is
  straightforward. For example, a single line in the VisTrails
  start-up file is needed to import all of VTK's classes.
* *Scalable Derivation of Data Products and Parameter Exploration.*  
  |vistrails| supports a series of operations
  for the simultaneous generation of multiple data products, including
  an interface that allows you to specify sets of values for
  different parameters in a workflow. The results of a parameter
  exploration can be displayed side by side in the VisTrails
  Spreadsheet for easy comparison.
* *Task Creation by Analogy.*  Analogies are supported as
  first-class operations to guide semi-automated changes to multiple
  workflows, without requiring you to directly manipulate or edit
  the workflow specifications.

Obtaining the software
""""""""""""""""""""""

Visit http://www.vistrails.org to access the VisTrails community
website. Here you will find information including instructions for
obtaining the software, online documentation, video tutorials, and
pointers to papers and presentations.

VisTrails is available as open
source; it is released under the GPL 2.0 license.  The pre-compiled
versions for Windows and Mac OS X come with an installer and
include a number of packages, including VTK, matplotlib, and Image
Magick. Additional packages, including packages written by users, are
also available (|eg| ITK, Matlab, Metro). Developers can easily add new
packages using the VisTrails plugin infrastructure. 