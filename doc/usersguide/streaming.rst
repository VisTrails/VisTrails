.. _chap-streaming:

**********************
Streaming in VisTrails
**********************

Streaming data may be useful for  a number of reasons, such as to incrementally
update  a  visualization,  or  to  process  more data  than  fit  into  memory.
VisTrails supports streaming data through the workflow. By implementing modules
that supports streaming,  data items will be passed  through the whole workflow
one at a time.

Using Streaming
===============

Streaming     is     similar      to     list     handling     (see     Chapter
:ref:`chap-list_handling`). Modules  that create  streams should output  a port
with list depth 1. Downstream modules that do not accept lists will be executed
once for  each item  in the  stream. Modules with  multiple input  streams will
combine them  pairwise. For  this reason the  input streams should  contain the
same number of items (or ben unlimited).

Modules accepting  a type with  list depth 1,  but does not  support streaming,
will convert input streams to lists and execute after the streaming have ended.

.. topic:: Try it Now!

  Lets use PythonSources to create  a simple example that incrementally sums up
  a  sequence of  numbers.  First  we  will create  a module  that streams  the
  natural  numbers  up  to  some  value.   Create a  new  workflow  and  add  a
  ``PythonSource``  module. Give  it an  input  port named  ``inputs`` of  type
  Integer, which  will specify the maxim  number to stream, and  an output port
  named ``out`` of type ``Integer`` with list depth 1, which will be the output
  stream.      An    output     stream    can     be    created     by    using
  ``self.set_streaming_output``, which takes the port name, an iterator object,
  and an optional length of the  input items.  To create an integer iterator we
  can use xrange. Add this to the PythonSource:

.. code-block:: python

   self.set_streaming_output('out',
                             xrange(inputs).__iter__(),
                             inputs)

.. topic:: Next Step!

  Now lets create a  module that captures the item in the  string. Add a second
  ``PythonSource`` module  below the  first one.  Give  it an input  port named
  ``integerStream`` of  type Integer and  list depth 1  that will be  our input
  stream.   An  input  stream  can  be  captured by  adding  the  magic  string
  ``#STREAMING``  to the PYthonSource  code and  calling ``self.set_streaming``
  with a  generator method as argument.   The generator method  should take the
  module as  an input.  It should first  initialize its value, in  our case set
  ``intsum=0``.  Then it should receive the inputs in a loop ending with yield.
  In each iteration  the module will be  updated to contain a new  input in the
  stream. Similar to a normal module, the loop should:

  1. get inputs
  2. compute outputs
  3. set outputs
  4. call ``yield``
  
  Below is the complete example. Add it to the PythonSource.

.. code-block:: python

  #STREAMING - This tag is magic, do not change.

  def generator(module):
      intsum = 0
      while 1:
          i = module.get_input('integerStream')
          intsum += i
          print "Sum so far:", intsum
          yield

  self.set_streaming(generator)

.. topic:: Finally:

  Connect  the  two  PythonSource's,  set   ``inputs``  to  100  in  the  first
  PythonSource, open the  vistrails console and execute. See  how the output is
  printed to  the console  while the stream  runs and  how the progress  of the
  modules increase. The output should  look like this: :vtl:`(open in vistrails)
  <streaming.vt>`

.. code-block:: python
  
  Sum so far: 0
  Sum so far: 1
  Sum so far: 3
  ...
  Sum so far: 4851
  Sum so far: 4950
