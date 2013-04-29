SRCS := tetgen_wrap.cc

INCLUDES := -I/usr/include/python2.4 -I/scratch/mjc/tetgen-dev

CC := g++
CXXFLAGS := -fPIC
LIBS := -lpython2.4 -ltet

%.o :: %.cc
	$(CC) $(CXXFLAGS) -c -o $@ $(INCLUDES) $<


_TetGen.so: tetgen_wrap.o
	$(CC) $(CXXFLAGS) -shared -o _TetGen.so tetgen_wrap.o $(INCLUDES) -L . $(LIBS)

tetgen_wrap.cc:tetgen.i
	swig -v -o tetgen_wrap.cc $(INCLUDES) -python -c++ tetgen.i


