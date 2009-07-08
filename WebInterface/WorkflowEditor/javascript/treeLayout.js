function Tree() {

	this.nodes = new Array();
	this.maxLevel = 0;

	this.root = function(){
		return this.nodes[0];
	}

	this.addNode = function( parentNode, width, height, object ) {
		var newNode = new Node(width, height, object);
		this.nodes[this.nodes.length] = newNode;

		if ( parentNode != null ) parentNode.addChild(newNode);

		this.maxLevel = Math.max(this.maxLevel, newNode.level);
		return newNode;
	}

	this.boundingBox = function() {
		var kbb = new KeepBoundingBox();

		for ( var w in this.nodes ) {
			var node = this.nodes[w];
			kbb.addPoint( ( node.x - node.width ) / 2.0, ( node.y - node.height ) / 2.0);
			kbb.addPoint( ( node.x + node.width ) / 2.0, ( node.y + node.height ) / 2.0);
		}
		return kbb.getBoundingBox();
	}

	this.getMaxNodeHeightPerLevel = function() {
		var result = new Array();

		for ( var i = 0; i <= this.maxLevel; i++ ) result[i] = 0;

		var level = null;

		for ( var w in this.nodes ) {
			level = this.nodes[w].level;
			result[level] = Math.max( result[level], this.nodes[w].height );
		}

		return result;
	}

	return this;
}

function randomTree(n, k) {
	var p = new Array();
	var minIndex = null;
	var index = null;

	for ( var i = 0; i < n; i++ ) {
		minIndex = Math.max( i - k, 0 );
		index = Math.round( minIndex + ( Math.random() * ( i - 1 - minIndex ) ) );
		p[i] = index;
	}

	var t = new Tree();
	var nodes = new Array();

	var parent = null;
	var width = null;
	var height = null;

	for ( var i = 0; i < n; i++ ) {
		if ( i == 0 ) parent = null;
		else parent = nodes[ p[i] ];

		width = 5 + 10 * Math.random();
		height = 5 + 10 * Math.random();

		nodes[nodes.length] = t.addNode( parent, width, height, i );
	}

	return t;
}

function KeepBoundingBox() {

	this.minX = null;
	this.minY = null;
	this.maxX = null;
	this.maxY = null;

	this.size = 0;

	this.addPoint = function( x, y ) {
		if ( this.minX == null || this.minX > x ) this.minX = x;
		if ( this.minY == null || this.minY > y ) this.minY = y;
		if ( this.maxX == null || this.maxX < x ) this.maxX = x;
		if ( this.maxY == null || this.maxY < y ) this.maxY = y;

		this.size++;
	}

	this.getBoundingBox = function(){
		var boundingBox = new Array();
		boundingBox[0] = this.minX;
		boundingBox[1] = this.minY;
		boundingBox[2] = this.maxX - this.minX;
		boundingBox[3] = this.maxY - this.minY;
		return boundingBox;
	}

	return this;
}

function Node( width, height, object ) {
	this.width = width;
	this.height = height;
	this.object = object;

	this.children = new Array();
	this.parent = null;
	this.index = 0;

	this.level = 0;
	this.mod = 0;
	this.prelim = 0;
	this.ancestor = null;
	this.thread = null;
	this.change = 0;
	this.shift = 0;

	this.x = 0;
	this.y = 0;

	this.getNumChildren = function() {
		return this.children.length;
	}

	this.hasChild = function() {
		return this.children.length > 0;
	}

	this.addChild = function( node ) {
		this.children[this.children.length] = node;
		node.index = this.children.length - 1;
		node.parent = this;
		node.level = this.level + 1;
	}

	this.isLeaf = function() {
		return this.children.length == 0;
	}

	this.leftChild = function() {
		return this.children[0];
	}

	this.rightChild = function() {
		return this.children[this.children.length - 1];
	}

	this.leftSibling = function() {
		if ( this.index > 0 ) return this.parent.children[this.index - 1];
		else return null;
	}

	this.leftMostSibling = function() {
		if (this.parent != null) return this.parent.children[0];
		else return self;
	}

	this.isSiblingOf = function( v ) {
		return ( this.parent == v.parent && this.parent != null );
	}

	return this;
}

function TreeLayout( tree, vertical_alignment, xdistance, ydistance ) {
/*
	This code is based on the pseudo-code in the paper:
	
	Christoph Buchheim, Michael Junger, and Sebastian Leipert.
	Improving walker's algorithm to run in linear time.
	In Stephen G. Kobourov and Michael T. Goodrich, editors, Graph
	Drawing, volume 2528 of Lecture Notes in Computer Science, pages
	344-353. Springer, 2002.
	
	which is a faster way to compute the tree layout
	proposed by Walker than the algorithm described by him.
	The original paper is:
	
	John Q. Walker II.
	A node-positioning algorithm for general trees.
	Softw., Pract. Exper., 20(7):685-705, 1990.
*/

	this.top = 0;
	this.middle = 1;
	this.bottom = 2;

	this.tree = tree;
	this.xdistance = xdistance;
	this.ydistance = ydistance;
	this.vertical_alignment = vertical_alignment;

	this.treeLayout = function() {
		for ( var v in this.tree.nodes ) {
			v.mod = 0;
			v.thread = null;
			v.ancestor = v;
		}

		var r = this.tree.root();
		this.firstWalk(r);
		this.secondWalk( r, -r.prelim );
		this.setVerticalPositions();
	}

	this.setVerticalPositions = function(){
		var maxNodeHeightPerLevel = this.tree.getMaxNodeHeightPerLevel();
		var info_level = new Array();

		var height_level = null;
		var position_level = 0;

		for ( var level in maxNodeHeightPerLevel ) {
			height_level = maxNodeHeightPerLevel[level];
			info_level[ level ] = new Array();
			info_level[ level ][0] = position_level;
			info_level[ level ][1] = height_level;
			position_level += ( this.ydistance + height_level );
		}

		var level = null;
		var nodes = this.tree.nodes;

		for ( var w in nodes ) {
			var node = nodes[w];
			level = node.level;
			position_level = info_level[level][0];
			height_level = info_level[level][1];


			if ( this.vertical_allignment == this.TOP ) {
				node.y = position_level + ( node.height / 2.0 );
			}
			else if ( this.vertical_alignment == this.MIDDLE )
				node.y = position_level + ( height_level / 2.0 );
			else // bottom
				node.y = position_level + height_level - ( node.height / 2.0 )
		}
	}

	this.gap = function( v1, v2 ) {
		return this.xdistance + ( ( v1.width + v2.width ) / 2.0 );
	}

	this.firstWalk = function( v ) {

		if ( v.isLeaf() ) {
			v.prelim = 0;

			var w = v.leftSibling();

			if ( w != null ) {
				v.prelim = w.prelim + this.gap( w, v );
			}

		} else {
			var defaultAncestor = v.leftChild();

			for ( var w in v.children ) {
				var node = v.children[w];
				this.firstWalk(node);
				defaultAncestor = this.apportion( node, defaultAncestor );
			}

			this.executeShifts(v);

			midpoint = ( v.leftChild().prelim + v.rightChild().prelim ) / 2.0;

			var ls = v.leftSibling();

			if ( ls != null ) {
				v.prelim = ls.prelim + this.gap( ls, v );
				v.mod = v.prelim - midpoint;
			} else {
				v.prelim = midpoint;
			}
		}
	}

	this.apportion = function( v, defaultAncestor ) {
/*
		Apportion: to divide and assign proportionally.

		Suppose everything is right. Now align the 
		subtree with root v to its parent node (note:
		the right alignment are encoded in the auxiliar
		variables, but the x and y are not correct; only
		in the end the correct values are assigned to x 
		and y). By property (*) in Section 4 the gratest 
		distinct ancestor of a node "w" in the 
		subtrees at rooted at the left siblings of "v"
		is w.ancestor if this value is a left sibling
		of v otherwise it is defaultAncestor.
*/
		var w = v.leftSibling()

		if ( w != null ) {
			// p stands for + or plus (right subtree)
			// m stands for - or minus (left subtree)
			// i stands for inside
			// o stands for outside
			// v stands for vertex
			// s stands for shift

			var vip = vop = v;
			var vim = w;
			var vom = vip.leftMostSibling();
			var sip = vip.mod;
			var sop = vop.mod;
			var sim = vim.mod;
			var som = vom.mod;

			while ( this.nextRight(vim) != null && this.nextLeft(vip) != null ) {

				vim = this.nextRight(vim);
				vip = this.nextLeft(vip);
				vom = this.nextLeft(vom);
				vop = this.nextRight(vop);

				vop.ancestor = v;

				var shift = ( vim.prelim + sim ) - ( vip.prelim + sip ) + this.gap( vim, vip );

				if ( shift > 0 ) {
					// Some problem with ancestor returning undefined.
					this.moveSubtree( this.ancestor( vim, v, defaultAncestor ), v, shift );
					sip += shift;
					sop += shift;
				}

				sim += vim.mod;
				sip += vip.mod;
				som += vom.mod;
				sop += vop.mod;
			}

			if ( this.nextRight( vim ) != null && this.nextRight( vop ) == null ) {
				vop.thread = this.nextRight( vim );
				vop.mod += sim - sop;
			}

			if ( this.nextLeft( vip ) != null && this.nextLeft( vom ) == null ) {
				vom.thread = this.nextLeft(vip);
				vom.mod += sip - som;
				defaultAncestor = v;
			}
		}

		return defaultAncestor;
	}

	this.nextLeft = function( v ) {
		if ( v.hasChild() ) return v.leftChild();
		else return v.thread;
	}

	this.nextRight = function( v ) {
		if ( v.hasChild() ) return v.rightChild();
		else return v.thread;
	}

	this.moveSubtree = function( wm, wp, shift ) {
		var subtrees = wp.index - wm.index;
		wp.change += -shift / subtrees;
		wp.shift += shift;
		wm.change += shift / subtrees;
		wp.prelim += shift;
		wp.mod += shift;
	}

	this.executeShifts = function( v ) {
		var shift = 0;
		var change = 0;

		for ( var i = v.getNumChildren() - 1; i >= 0; i-- ) {
			var w = v.children[i];
			w.prelim += shift;
			w.mod += shift;
			change += w.change;
			shift += w.shift + change;
		}
	}

	this.ancestor = function( vim, v, defaultAncestor ) {

		if (vim.ancestor != null) {
			if ( vim.ancestor.isSiblingOf( v ) ) return vim.ancestor;
		}

		return defaultAncestor;
	}

	this.secondWalk = function( v, m ) {
		v.x = v.prelim + m;
		for ( var w in v.children ) {
			this.secondWalk( v.children[w], m + v.mod );
		}
	}

	this.treeLayout();

	return this;
}

function testTree() {
	var t = new randomTree(50, 50); //new Tree();

	var a = t.addNode(null,1,1,"a");

	var b = t.addNode(a,1,1,"b")
	var c = t.addNode(a,1,1,"c")
	var d = t.addNode(a,1,1,"d")
	
	var e = t.addNode(b,1,1,"e")
	var f = t.addNode(b,1,1,"f")
	var g = t.addNode(d,1,1,"g")
	var h = t.addNode(d,1,1,"h")
	
	var i = t.addNode(f,1,1,"i")
	var j = t.addNode(f,1,1,"j")
	var k = t.addNode(h,1,1,"k")
	var l = t.addNode(h,1,1,"l")
	var m = t.addNode(h,1,1,"m")
	var n = t.addNode(h,1,1,"n")
	var o = t.addNode(h,1,1,"o")

	return new TreeLayout(t, 100, 100, 100);
}
