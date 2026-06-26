var $$$ = {};

/*=====================================================
Math
=====================================================*/

$$$.rand = function( min, max ) {
	return Math.random() * ( max - min ) + min;
};

/*=====================================================
Particle
=====================================================*/

$$$.Part = function() {
	this.reset();
};

$$$.Part.prototype.reset = function() {
	this.x = 0;
	this.y = 0;
	this.z = 0;
	this.vx = $$$.rand( -0.5, 0.5 );
	this.vy = $$$.rand( -0.5, 0.5 );
	this.vz = $$$.rand( -0.25, 0.5 ) ;
	this.s = 0;
	this.sx = 0;
	this.sy = 0;
	this.life = 1;
	this.decay = $$$.rand( 0.005, 0.02 );
	this.radius = $$$.rand( 5, 15 );
	this.sradius = this.radius;
	this.rradius = this.radius;
	this.hue = 0;
	this.alpha = 1;
	this.angle = 0;
};

$$$.Part.prototype.step = function() {
	if( $$$.mouse && $$$.mouse.down ) {
		this.vx *= 1.1;
		this.vy *= 1.1;
		this.vz *= 1.1;
	} else {
		this.vx *= 1.04;
		this.vy *= 1.04;
		this.vz *= 1.04;
	}

	this.x += this.vx;
	this.y += this.vy;
	this.z += this.vz;
	this.s = $$$.fl / ( $$$.fl + this.z );
	this.sx = this.x * this.s;
	this.sy = this.y * this.s;
	this.sradius = this.radius * this.s;
	this.rradius = Math.max( 0.0001, this.sradius * this.life );
	this.angle = Math.atan2( this.sy, this.sx );
	this.hue = ( this.angle / ( Math.PI * 2 ) ) * 180 + $$$.tick * 4;
	this.alpha = this.life;

	if( this.z < $$$.bounds.z.min ) {
		this.reset();
		return;
	}

	if( this.life > 0 ) {
		this.life -= this.decay;
	} else {
		this.reset();
	}
};

$$$.Part.prototype.draw = function() {
	$$$.ctx.beginPath();
	$$$.ctx.arc( this.sx, this.sy, this.rradius * 2, 0, Math.PI * 2 );
	$$$.ctx.fillStyle = 'hsla(' + ( this.hue + 60 ) + ', 60%, 30%, ' + this.alpha / 3 + ')';
	$$$.ctx.fill();
	$$$.ctx.strokeStyle = 'hsla(' + ( this.hue - 60 ) + ', 60%, 30%, ' + this.alpha / 2 + ')';
	$$$.ctx.stroke();

	var angle1 = this.angle + Math.PI / 2,
		angle2 = this.angle,
		angle3 = this.angle - Math.PI / 2;

	$$$.ctx.beginPath();
	$$$.ctx.moveTo( 0, 0 );
	$$$.ctx.lineTo( this.sx + Math.cos( angle1 ) * this.rradius, this.sy + Math.sin( angle1 ) * this.rradius );
	$$$.ctx.lineTo( this.sx + Math.cos( angle2 ) * this.rradius * 6, this.sy + Math.sin( angle2 ) * this.rradius * 6 );
	$$$.ctx.lineTo( this.sx + Math.cos( angle3 ) * this.rradius, this.sy + Math.sin( angle3 ) * this.rradius );
	$$$.ctx.closePath();
	$$$.ctx.fillStyle = 'hsla(' + this.hue + ', 50%, 30%, ' + this.alpha / 2 + ')';
	$$$.ctx.fill();

	$$$.ctx.beginPath();
	$$$.ctx.moveTo( this.sx + Math.cos( angle2 ) * this.rradius * 6, this.sy + Math.sin( angle2 ) * this.rradius * 6 );
	$$$.ctx.lineTo( 0, 0 );
	$$$.ctx.strokeStyle = 'hsla(' + this.hue + ', 50%, 30%, ' + this.alpha + ')';
	$$$.ctx.stroke();

	var sparkleRadius = this.rradius * 4;
	$$$.ctx.fillStyle = 'hsla(' + ( this.hue + 180 ) + ', 100%, 50%, ' + this.alpha * 2 + ')';
	$$$.ctx.fillRect( ( this.sx + $$$.rand( -sparkleRadius, sparkleRadius ) ), ( this.sy + $$$.rand( -sparkleRadius, sparkleRadius ) ), 1, 1 );
};

/*=====================================================
General
=====================================================*/

$$$.init = function() {
	$$$.stop( true );
	$$$.canvas = document.createElement( 'canvas' );
	$$$.ctx = $$$.canvas.getContext( '2d' );
	$$$.parts = [];
	$$$.mouse = {
		down: 0
	};
	var origin_item = document.getElementById('galleryMusicCanvasFrame') ||
		document.getElementById('musicCanvasFrame') ||
		document.body.getElementsByClassName('blog-content')[0] ||
		document.body;
	origin_item.appendChild($$$.canvas);
	$$$.canvas.className = 'canvas_container';
	$$$.reset();
	$$$.running = true;
	$$$.loop();
};

$$$.__del = function(){
	$$$.stop( true );
}

$$$.stop = function( removeCanvas ){
	$$$.running = false;
	if( $$$.raf ) {
		cancelAnimationFrame( $$$.raf );
		$$$.raf = null;
	}
	if( removeCanvas && $$$.canvas && $$$.canvas.parentNode ) {
		$$$.canvas.parentNode.removeChild( $$$.canvas );
	}
	if( removeCanvas ) {
		$$$.canvas = null;
		$$$.ctx = null;
	}
	$$$.parts = [];
}

$$$.reset = function() {
	if( !$$$.canvas ) {
		return;
	}
	$$$.tick = 0;
	$$$.width = window.innerWidth;
	$$$.height = window.innerHeight;
	$$$.canvas.width = $$$.width;
	$$$.canvas.height = $$$.height;
	$$$.mouse = $$$.mouse || {};
	$$$.mouse.down = 0;
	$$$.fl = 300;
	$$$.bounds = {
		x: { min: -$$$.width / 2, max: $$$.width / 2 },
		y: { min: -$$$.height / 2, max: $$$.height / 2 },
		z: { min: -$$$.fl, max: 1000 }
	};
	$$$.parts = $$$.parts || [];
	$$$.parts.length = 0;
};

$$$.step = function() {
	$$$.parts = $$$.parts || [];
	$$$.tick = $$$.tick || 0;
	$$$.bounds = $$$.bounds || {
		x: { min: -window.innerWidth / 2, max: window.innerWidth / 2 },
		y: { min: -window.innerHeight / 2, max: window.innerHeight / 2 },
		z: { min: -300, max: 1000 }
	};
	if( $$$.tick % 2 == 0 ) {
		if( $$$.parts.length < 200 ) {
			$$$.parts.push( new $$$.Part() );
		}
	}
	var i = $$$.parts.length;
	while( i-- ) {
		$$$.parts[ i ].step();
	}
	if( $$$.mouse && $$$.mouse.down ) {
		$$$.tick += 3;
	} else {
		$$$.tick += 1;
	}
};

$$$.draw = function() {
	if( !$$$.ctx || !$$$.canvas || !$$$.parts ) {
		return;
	}
	$$$.ctx.globalCompositeOperation = 'destination-out';
	$$$.ctx.fillStyle = 'hsla(0, 0%, 0%, 0.6)';
	$$$.ctx.fillRect( 0, 0, $$$.width, $$$.height );
	$$$.ctx.globalCompositeOperation = 'lighter';
	$$$.ctx.save();
	$$$.ctx.translate( $$$.width / 2, $$$.height / 2 );
	$$$.ctx.rotate( $$$.tick / 300 );
	var i = $$$.parts.length;
	while( i-- ) {
		$$$.parts[ i ].draw();
	}
	$$$.ctx.restore();
};

$$$.loop = function() {
	if( !$$$.running ) {
		return;
	}
	$$$.raf = requestAnimationFrame( $$$.loop );
	$$$.step();
	$$$.draw();
};

/*=====================================================
Events
=====================================================*/

$$$.resize = function() {
	if( !$$$.running || !$$$.canvas ) {
		return;
	}
	$$$.reset();
};

$$$.mousedown = function() {
	$$$.mouse = $$$.mouse || {};
	$$$.mouse.down = 1;
};

$$$.mouseup = function() {
	$$$.mouse = $$$.mouse || {};
	$$$.mouse.down = 0;
};

window.addEventListener( 'resize', $$$.resize );
window.addEventListener( 'mousedown', $$$.mousedown );
window.addEventListener( 'mouseup', $$$.mouseup );
//
// $$$.init();
