%module TetGen
%{
#include <tetgen.h>
%}

class tetgenio {

  public:

    // Maximum number of characters in a file name (including the null).
    enum {FILENAMESIZE = 1024};

    // Maxi. numbers of chars in a line read from a file (incl. the null).
    enum {INPUTLINESIZE = 1024};

    // The polygon data structure.  A "polygon" is a planar polygon. It can
    //   be arbitrary shaped (convex or non-convex) and bounded by non-
    //   crossing segments, i.e., the number of vertices it has indictes the
    //   same number of edges.
    // 'vertexlist' is a list of vertex indices (integers), its length is
    //   indicated by 'numberofvertices'.  The vertex indices are odered in
    //   either counterclockwise or clockwise way.
  
    class polygon;

    static void init(polygon* p) {
      p->vertexlist = (int *) NULL;
      p->numberofvertices = 0;
    }

    // The facet data structure.  A "facet" is a planar facet.  It is used
    //   to represent a planar straight line graph (PSLG) in two dimension.
    //   A PSLG contains a list of polygons. It also may conatin holes in it,
    //   indicated by a list of hole points (their coordinates).
    class facet;

    static void init(facet* f) {
      f->polygonlist = (polygon *) NULL;
      f->numberofpolygons = 0;
      f->holelist = (REAL *) NULL;
      f->numberofholes = 0;
    }

    // The periodic boundary condition group data structure.  A "pbcgroup"
    //   contains the definition of a pbc and the list of pbc point pairs.
    //   'fmark1' and 'fmark2' are the facetmarkers of the two pbc facets f1
    //   and f2, respectively. 'transmat' is the transformation matrix which
    //   maps a point in f1 into f2.  An array of pbc point pairs are saved
    //   in 'pointpairlist'. The first point pair is at indices [0] and [1],
    //   followed by remaining pairs. Two integers per pair.
    class pbcgroup;
  public:

    // Items are numbered starting from 'firstnumber' (0 or 1), default is 0.
    int firstnumber; 

    // Dimension of the mesh (2 or 3), default is 3.
    int mesh_dim;

    // `pointlist':  An array of point coordinates.  The first point's x
    //   coordinate is at index [0] and its y coordinate at index [1], its
    //   z coordinate is at index [2], followed by the coordinates of the
    //   remaining points.  Each point occupies three REALs. 
    // `pointattributelist':  An array of point attributes.  Each point's
    //   attributes occupy `numberofpointattributes' REALs. 
    // 'addpointlist':  An array of additional point coordinates.
    // 'addpointattributelist':  An array of attributes for addition points.
    // `pointmarkerlist':  An array of point markers; one int per point.
    REAL *pointlist;
    REAL *pointattributelist;
    REAL *addpointlist;
    REAL *addpointattributelist;
    int *pointmarkerlist;
    int numberofpoints;
    int numberofpointattributes;
    int numberofaddpoints;
 
    // `elementlist':  An array of element (triangle or tetrahedron) corners. 
    //   The first element's first corner is at index [0], followed by its
    //   other corners in counterclockwise order, followed by any other
    //   nodes if the element represents a nonlinear element.  Each element
    //   occupies `numberofcorners' ints.
    // `elementattributelist':  An array of element attributes.  Each
    //   element's attributes occupy `numberofelementattributes' REALs.
    // `elementconstraintlist':  An array of constraints, i.e. triangle's
    //   area or tetrahedron's volume; one REAL per element.  Input only.
    // `neighborlist':  An array of element neighbors; 3 or 4 ints per
    //   element.  Output only.
    int *tetrahedronlist;
    REAL *tetrahedronattributelist;
    REAL *tetrahedronvolumelist;
    int *neighborlist;
    int numberoftetrahedra;
    int numberofcorners;
    int numberoftetrahedronattributes;

    // `facetlist':  An array of facets.  Each entry is a structure of facet.
    // `facetmarkerlist':  An array of facet markers; one int per facet.
    facet *facetlist;
    int *facetmarkerlist;
    int numberoffacets;

    // `holelist':  An array of holes.  The first hole's x, y and z
    //   coordinates  are at indices [0], [1] and [2], followed by the
    //   remaining holes. Three REALs per hole. 
    REAL *holelist;
    int numberofholes;

    // `regionlist': An array of regional attributes and volume constraints.
    //   The first constraint's x, y and z coordinates are at indices [0],
    //   [1] and [2], followed by the regional attribute at index [3], foll-
    //   owed by the maximum volume at index [4]. Five REALs per constraint. 
    // Note that each regional attribute is used only if you select the `A'
    //   switch, and each volume constraint is used only if you select the
    //   `a' switch (with no number following).
    REAL *regionlist;
    int numberofregions;

    // `facetconstraintlist': An array of facet maximal area constraints.
    //   Two REALs per constraint. The first one is the facet marker (cast
    //   it to int), the second is its maximum area bound.
    // Note the 'facetconstraintlist' is used only for the 'q' switch. 
    REAL *facetconstraintlist;
    int numberoffacetconstraints;

    // `segmentconstraintlist': An array of segment max. length constraints.
    //   Three REALs per constraint. The first two are the indices (pointing
    //   into 'pointlist') of the endpoints of the segment, the third is its
    //   maximum length bound.
    // Note the 'segmentconstraintlist' is used only for the 'q' switch. 
    REAL *segmentconstraintlist;
    int numberofsegmentconstraints;

    // `nodeconstraintlist':  An array of segment length constraints.  Two
    //   REALs per constraint. The first one is the index (pointing into
    //   'pointlist') of the node, the second is its edge length bound.
    // Note the 'nodeconstraintlist' is used only for the 'q' switch. 
    REAL *nodeconstraintlist;
    int numberofnodeconstraints;

    // 'pbcgrouplist':  An array of periodic boundary condition groups.
    pbcgroup *pbcgrouplist;
    int numberofpbcgroups;

    // `trifacelist':  An array of triangular face endpoints.  The first
    //   face's endpoints are at indices [0], [1] and [2], followed by the
    //   remaining faces.  Three ints per face.
    // `adjtetlist':  An array of adjacent tetrahedra to the faces of
    //   trifacelist. Each face has at most two adjacent tets, the first
    //   face's adjacent tets are at [0], [1]. Two ints per face. A '-1'
    //   indicates outside (no adj. tet). This list is output when '-n'
    //   switch is used.
    // `trifacemarkerlist':  An array of face markers; one int per face.
    int *trifacelist;
    int *adjtetlist;
    int *trifacemarkerlist;
    int numberoftrifaces;

    // `edgelist':  An array of edge endpoints.  The first edge's endpoints
    //   are at indices [0] and [1], followed by the remaining edges.  Two
    //   ints per edge.
    // `edgemarkerlist':  An array of edge markers; one int per edge.
    int *edgelist;
    int *edgemarkerlist;
    int numberofedges;

  public:

    // Initialize routine.
    void initialize();
    void deinitialize();

    // Input & output routines.
    bool load_node_call(FILE* infile, int markers, char* nodefilename);
    bool load_node(char* filename);
    bool load_addnodes(char* filename);
    bool load_pbc(char* filename);
    bool load_var(char* filename);
    bool load_mtr(char* filename);
    bool load_poly(char* filename);
    bool load_off(char* filename);
    bool load_ply(char* filename);
    bool load_stl(char* filename);
    bool load_medit(char* filename);
    bool load_plc(char* filename, int object);
    bool load_tetmesh(char* filename);
    void save_nodes(char* filename);
    void save_elements(char* filename);
    void save_faces(char* filename);
    void save_edges(char* filename);
    void save_neighbors(char* filename);
    void save_poly(char* filename);

    // Read line and parse string functions.
    char *readline(char* string, FILE* infile, int *linenumber);
    char *findnextfield(char* string);
    char *readnumberline(char* string, FILE* infile, char* infilename);
    char *findnextnumber(char* string);

    // Constructor and destructor.
    tetgenio() {initialize();}
    ~tetgenio() {deinitialize();}
};

%rename(polygon) tetgenio::polygon;
%rename(facet) tetgenio::facet;
%rename(pbcgroup) tetgenio::pbcgroup;

class tetgenio::polygon {
  int *vertexlist;
  int numberofvertices;
};

class tetgenio::facet {
  polygon *polygonlist;
  int numberofpolygons;
  REAL *holelist;
  int numberofholes;
};

class tetgenio::pbcgroup {
  int fmark1, fmark2;
  REAL transmat[4][4];
  int numberofpointpairs;
  int *pointpairlist;
};


void tetrahedralize(char *switches, tetgenio &in, tetgenio &out);


// additional interface for data loading.
REAL* allocate_array(unsigned int sz);
void set_val(REAL*arr, unsigned int idx, float val);
float get_val(REAL*arr, unsigned int idx);
tetgenio::facet* allocate_facet_array(unsigned int sz);
void add_tri(tetgenio::facet*arr, int fidx, int nidx0, int nidx1, int nidx2); 

%{
#include <iostream>
using namespace std;

REAL* allocate_array(unsigned int sz)
{
  return new REAL[sz];
}

void set_val(REAL*arr, unsigned int idx, float val)
{	
  arr[idx] = val;
}
float get_val(REAL*arr, unsigned int idx)
{	
  return arr[idx];
}

tetgenio::facet* allocate_facet_array(unsigned int sz)
{
  return new tetgenio::facet[sz];
}

void add_tri(tetgenio::facet*arr, int fidx, int nidx0, int nidx1, int nidx2)
{
  tetgenio::facet *f = &arr[fidx];
  f->numberofpolygons = 1;	
  f->polygonlist = new tetgenio::polygon[f->numberofpolygons];
  f->numberofholes = 0;
  f->holelist = 0;
  tetgenio::polygon *p = &f->polygonlist[0];
  p->numberofvertices = 3;
  p->vertexlist = new int[p->numberofvertices];
  p->vertexlist[0] = nidx0;
  p->vertexlist[1] = nidx1;
  p->vertexlist[2] = nidx2;
}



void tetrahedralize(char* switches, tetgenio &in, tetgenio &out)
{
  tetrahedralize(switches, &in, &out);
}

%}