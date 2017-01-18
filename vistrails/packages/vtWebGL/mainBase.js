var canvas;
var gl;

// MATRICES
var mvMatrix;
var perspectiveMatrix;

// SHADER PROGRAM
var shaderColor;
var shaderTexture;
var shaderLine;

// CAMERA
var rotMatrix;
var translation = [0.0, 0.0, 0.0];
var objScale = 1.0;
var lastMouseX = null;
var lastMouseY = null;
var mouseDown = false;
var center = [0, 0, -1];
var eye = [0, 0, 0];
var up = [0, 1, 0];

// GEOMETRY
//var renderingObjs = [null];
var vbuff = [null, null, null, null, null]; //MESH BUFF
var lbuff = [null, null, null, null, null]; //LINE BUFF
var VERTEX  = 0;
var INDEX   = 1;
var NORMAL  = 2;
var COLOR   = 3;
var TEXTURE = 4;

//TEXTURE
var texture;

// OTHERS
var baseTextureImg;

// Initialize WebGL, returning the GL context or null if
// WebGL isn't available or could not be initialized.
function initWebGL() {
  gl = null;
  
  rotMatrix = Matrix.I(4);
  try {
    gl = canvas.getContext("experimental-webgl");
    gl.viewportWidth = canvas.width;
    gl.viewportHeight = canvas.height;
  } catch(e) {}
  
  // If we don't have a GL context, give up now  
  if (!gl) {
    alert("Unable to initialize WebGL. Your browser may not support it.");
  }

  initMesh();
}

// Initialize the buffers of the geometry
function initBuffers() { 
  createBuffers()
}


// Initialize the shaders of our scene
function initShaders() {
  var vertexColor     = getShader(gl, "shader-vs-COLOR");
  var fragmentColor   = getShader(gl, "shader-fs-COLOR");
  var vertexTexture   = getShader(gl, "shader-vs-TEXTURE");
  var fragmentTexture = getShader(gl, "shader-fs-TEXTURE");
  var vertexLine      = getShader(gl, "shader-vs-LINE");
  var fragmentLine    = getShader(gl, "shader-fs-LINE");
  
  // Create the Color Shader Program
  shaderColor = gl.createProgram();
  gl.attachShader(shaderColor, vertexColor);
  gl.attachShader(shaderColor, fragmentColor);
  gl.linkProgram(shaderColor);

  // Create the Texture Shader Program
  shaderTexture = gl.createProgram();
  gl.attachShader(shaderTexture, vertexTexture);
  gl.attachShader(shaderTexture, fragmentTexture);
  gl.linkProgram(shaderTexture);

  // Create the Line Shader Program
  shaderLine = gl.createProgram();
  gl.attachShader(shaderLine, vertexLine);
  gl.attachShader(shaderLine, fragmentLine);
  gl.linkProgram(shaderLine);
  
  // If creating the shader program failed, alert
  if (!gl.getProgramParameter(shaderColor, gl.LINK_STATUS) || 
      !gl.getProgramParameter(shaderTexture, gl.LINK_STATUS) ||
      !gl.getProgramParameter(shaderLine, gl.LINK_STATUS)) {
    alert("Unable to initialize the shader program.");
  } 
}

function setShader(s, isTextured) {
  gl.useProgram(s);  
  s.vertexPositionAttribute = gl.getAttribLocation(s, "aVertexPosition");
  gl.enableVertexAttribArray(s.vertexPositionAttribute);
  s.vertexNormalAttribute = gl.getAttribLocation(s, "aVertexNormal");
  gl.enableVertexAttribArray(s.vertexNormalAttribute);  
  s.vertexColorAttribute = gl.getAttribLocation(s, "aVertexColor");
  gl.enableVertexAttribArray(s.vertexColorAttribute);

  if (isTextured){
    s.textureCoordAttribute = gl.getAttribLocation(s, "aTextureCoord");
    gl.enableVertexAttribArray(s.textureCoordAttribute);
    s.samplerUniform = gl.getUniformLocation(s, "uSampler");  
  }

  s.useLightingUniform = gl.getUniformLocation(s, "uUseLighting");

  s.pUniform = gl.getUniformLocation(s, "uPMatrix");
  s.mvUniform = gl.getUniformLocation(s, "uMVMatrix");
  s.nUniform = gl.getUniformLocation(s, "uNMatrix");   
}

// getShader
//
// Loads a shader program by scouring the current document,
// looking for a script with the specified ID.
function getShader(gl, id) {
  var shaderScript = document.getElementById(id);
  
  // Didn't find an element with the specified ID; abort.  
  if (!shaderScript) {
    return null;
  }
  
  // Walk through the source element's children, building the
  // shader source string.  
  var theSource = "";
  var currentChild = shaderScript.firstChild;
  
  while(currentChild) {
    if (currentChild.nodeType == 3) {
      theSource += currentChild.textContent;
    }
    
    currentChild = currentChild.nextSibling;
  }
  
  // Now figure out what type of shader script we have,
  // based on its MIME type.  
  var shader;
  
  if (shaderScript.type == "x-shader/x-fragment") {
    shader = gl.createShader(gl.FRAGMENT_SHADER);
  } else if (shaderScript.type == "x-shader/x-vertex") {
    shader = gl.createShader(gl.VERTEX_SHADER);
  } else {
    return null;  // Unknown shader type
  }
  
  // Send the source to the shader object  
  gl.shaderSource(shader, theSource);
  
  // Compile the shader program  
  gl.compileShader(shader);
  
  // See if it compiled successfully  
  if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
    alert("An error occurred compiling the shaders: " + gl.getShaderInfoLog(shader));
    return null;
  }
  
  return shader;
}

function handleMouseDown(event) {
  mouseDown = true;
  lastMouseX = event.clientX;
  lastMouseY = event.clientY;
}


function handleMouseUp(event) {
  mouseDown = false;
}


function handleMouseMove(event) {
  if (!mouseDown) {
    return;
  }
  var step = 5;
  var newX = event.clientX;
  var newY = event.clientY;
  var deltaX = newX - lastMouseX
  var deltaY = newY - lastMouseY;

  if (event.button == 0){
    var rX = deltaX / (step*objScale) * Math.PI / 180.0;  
    var rY = deltaY / (step*objScale) * Math.PI / 180.0;  
    var mx = Matrix.Rotation(rX, $V([0, 1, 0])).ensure4x4();
    var my = Matrix.Rotation(rY, $V([1, 0, 0])).ensure4x4();
    mx = mx.x(my);
    rotMatrix = mx.x(rotMatrix);
  } else if (event.button == 1){
    var tx = (deltaX / objScale)/1000;
    var ty = (deltaY / objScale)/1000;
    translation[0] += tx;
    translation[1] -= ty;
  } else {
    objScale = objScale+(deltaX-deltaY)/1000.0;
  }

  lastMouseX = newX
  lastMouseY = newY;
}

function setMatrixUniforms() {
  //shaderColor
  gl.useProgram(shaderColor);
  gl.uniformMatrix4fv(shaderColor.pUniform, false, new Float32Array(perspectiveMatrix.flatten()));
  gl.uniformMatrix4fv(shaderColor.mvUniform, false, new Float32Array(mvMatrix.flatten()));

  var normal = mvMatrix.inverse();
  normal = normal.transpose();
  gl.uniformMatrix4fv(shaderColor.nUniform, false, new Float32Array(normal.flatten()));

  //shaderTexture
  gl.useProgram(shaderTexture);
  gl.uniformMatrix4fv(shaderTexture.pUniform, false, new Float32Array(perspectiveMatrix.flatten()));
  gl.uniformMatrix4fv(shaderTexture.mvUniform, false, new Float32Array(mvMatrix.flatten()));
  gl.uniformMatrix4fv(shaderTexture.nUniform, false, new Float32Array(normal.flatten()));

  //shaderLine
  gl.useProgram(shaderLine);
  gl.uniformMatrix4fv(shaderLine.pUniform, false, new Float32Array(perspectiveMatrix.flatten()));
  gl.uniformMatrix4fv(shaderLine.mvUniform, false, new Float32Array(mvMatrix.flatten()));
}

createBuffers = function() {
  for (i=0; i<renderingCount; i++)
    renderingObjs[i].createBuffers();
}

//Render the objects of the scene
renderObj = function () {
  // Render
  mvPushMatrix();
    camerapos = [center[0]*-1, center[1]*-1, center[2]*-1];
    mtrans = [-translation[0], -translation[1], -translation[2]];
    m1 = cameraRotation(eye[0], eye[1], eye[2], center[0], center[1], center[2], up[0], up[1], up[2]);
    m2 = m1.transpose();
    
    mvTranslate(translation);
    mvTranslate(center);
    mvMatrix = mvMatrix.x(m2);

    mvScale([objScale, objScale, objScale]);    
    mvMatrix = mvMatrix.x(rotMatrix);

    mvMatrix = mvMatrix.x(m1);
    mvTranslate(camerapos);
    mvTranslate(mtrans);
    
    setMatrixUniforms();
    // Render
    for(i=0; i<renderingCount; i++){
      s = null;
      if (renderingObjs[i] instanceof Lines)
        s = shaderLine;
      else if(renderingObjs[i].isTextured)
        s = shaderTexture;    
      else
        s = shaderColor;

      setShader(s, renderingObjs[i].isTextured);
      renderingObjs[i].renderObj(s);
    }
  mvPopMatrix();
}

//Function call onLoad of the texture
function handleLoadedTexture(texture) {
  gl.bindTexture(gl.TEXTURE_2D, texture);
  gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, true);
  gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, texture.image);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
  gl.bindTexture(gl.TEXTURE_2D, null);
}

//Load and Initialize Texture
function initTexture() {  
  texture = null;
  gl.useProgram(shaderTexture);
  gl.enable(gl.TEXTURE_2D);
  texture = gl.createTexture();
  texture.image = new Image();
  texture.image.onload = function() {
    handleLoadedTexture(texture)
  }
  texture.image.src = "test.bmp";
}

//-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
// Matrix utility functions

function loadIdentity() {
  mvMatrix = Matrix.I(4);
}

function multMatrix(m) {
  mvMatrix = mvMatrix.x(m);
}

function mvTranslate(v) {
  multMatrix(Matrix.Translation($V([v[0], v[1], v[2]])).ensure4x4());
}

function mvScale(v) {
  multMatrix(Matrix.Scale($V([v[0], v[1], v[2]])).ensure4x4());
}

function mvRotate(angle, v) {
  var inRadians = angle * Math.PI / 180.0;
  
  var m = Matrix.Rotation(inRadians, $V([v[0], v[1], v[2]])).ensure4x4();
  multMatrix(m);
}

var mvMatrixStack = [];

function mvPushMatrix(m) {
  if (m) {
    mvMatrixStack.push(m.dup());
    mvMatrix = m.dup();
  } else {
    mvMatrixStack.push(mvMatrix.dup());
  }
}

function mvPopMatrix() {
  if (!mvMatrixStack.length) {
    throw("Can't pop from an empty matrix stack.");
  }
  
  mvMatrix = mvMatrixStack.pop();
  return mvMatrix;
}
