var hi=function(data,txt) {
  "use strict";
      var shock = document.createElement('div');
	  var textnode = document.createElement('div');
	  var temp=document.createTextNode(txt); //创建一个文本节点内容
	  textnode.appendChild(temp)

      var img = new Image;
      img.src = data;
      img.style.pointerEvents = "none";
      img.style.width = '300px';
      img.style.height = '300px';
      img.style.transition = '1s all';
      img.style.position = 'fixed';
      img.style.left = 'calc(50% - 150px)';
      img.style.bottom = '-100px';
      img.style.zIndex = 999999;


	  textnode.style.pointerEvents = "none";
	  textnode.style.align = "center";
      textnode.style.width = '300px';
      textnode.style.height = '300px';
      textnode.style.transition = '1s all';
      textnode.style.position = 'fixed';
      textnode.style.left = 'calc(50% - 150px)';
      textnode.style.bottom = '-100px';
      textnode.style.zIndex = 999999;
	  document.body.appendChild(textnode);
      document.body.appendChild(img);

      window.setTimeout(function(){
        img.style.bottom = '-50px';
		textnode.style.bottom = '-50px';
      },30);

      window.setTimeout(function(){
        img.style.bottom = '-300px';
		textnode.style.bottom = '-300px';
      }, 4300);
      window.setTimeout(function(){
        img.parentNode.removeChild(img);
		textnode.parentNode.removeChild(textnode);
      }, 5400);
};

var  penguin=function(data,txt) {

    var shock = document.createElement('div');
	var textnode = document.createElement('div');
	var temp=document.createTextNode(txt); //创建一个文本节点内容
	textnode.appendChild(temp);
    var img = new Image();
    img.src = data;
    img.style.pointerEvents = "none";
    img.style.width = '374px';
    img.style.height = '375px';
    img.style.transition = '13s all';
    img.style.position = 'fixed';
    img.style.right = '-374px';
    // img.style.bottom = 'calc(-50% + 280px)';
    img.style.bottom = '0px';
    img.style.zIndex = 999999;

    textnode.style.pointerEvents = "none";
    textnode.style.width = '374px';
    textnode.style.height = '375px';
    textnode.style.transition = '13s all';
    textnode.style.position = 'fixed';
    textnode.style.right = '-374px';
    // img.style.bottom = 'calc(-50% + 280px)';
    textnode.style.bottom = '0px';
    textnode.style.zIndex = 999999;

	document.body.appendChild(textnode);
    document.body.appendChild(img);

    window.setTimeout(function(){
      img.style.right = 'calc(100% + 500px)';
	  textnode.style.right = 'calc(100% + 500px)';
    }, 50);

    // window.setTimeout(function(){
    //   img.style.right = 'calc(100% + 375px)';
    // }, 4500);

    window.setTimeout(function(){
      img.parentNode.removeChild(img);
	  textnode.parentNode.removeChild(textnode);
    }, 10300);

  };


var lol = function(data,txt) {

    var shock = document.createElement('div');
	var textnode = document.createElement('div');
	var temp=document.createTextNode(txt); //创建一个文本节点内容
	textnode.appendChild(temp);
    var img = new Image;
    img.src = data;
    img.style.pointerEvents = "none";
    img.style.width = '240px';
    img.style.height = '200px';
    img.style.transition = '1s all';
    img.style.position = 'fixed';
    img.style.left = 'calc(50% - 125px)';
    img.style.bottom = '-250px';
    img.style.zIndex = 999999;

	textnode.style.pointerEvents = "none";
    textnode.style.width = '240px';
    textnode.style.height = '200px';
    textnode.style.transition = '1s all';
    textnode.style.position = 'fixed';
    textnode.style.left = 'calc(50% - 125px)';
    textnode.style.bottom = '-250px';
    textnode.style.zIndex = 999999;

	document.body.appendChild(textnode);
    document.body.appendChild(img);

    window.setTimeout(function(){
      img.style.bottom = '-10px';
	  textnode.style.bottom = '-10px';
    },50);

    window.setTimeout(function(){
      img.style.bottom = '-250px';
	  textnode.style.bottom = '-250px';
    }, 3300);

    window.setTimeout(function(){
      img.parentNode.removeChild(img);
      textnode.parentNode.removeChild(textnode);
    }, 5400);

 };

var fly = function(data,txt) {

    var shock = document.createElement('div');
	var textnode = document.createElement('div');
	var temp=document.createTextNode(txt); //创建一个文本节点内容
	textnode.appendChild(temp);
    var img = new Image();
    img.src = data;
    img.style.pointerEvents = "none";
    img.style.width = '500px';
    img.style.height = '375px';
    img.style.transition = '6s all';
    img.style.position = 'fixed';
    img.style.right = '-374px';
    img.style.bottom = '0px';
    img.style.zIndex = 999999;

	textnode.style.pointerEvents = "none";
    textnode.style.width = '500px';
    textnode.style.height = '375px';
    textnode.style.transition = '6s all';
    textnode.style.position = 'fixed';
    textnode.style.right = '-374px';
    textnode.style.bottom = '0px';
    textnode.style.zIndex = 999999;

	document.body.appendChild(textnode);
    document.body.appendChild(img);

    window.setTimeout(function(){
      img.style.right = 'calc(50% - 187px)';
	  textnode.style.right = 'calc(50% - 187px)';
    },50);

    window.setTimeout(function(){
      img.style.right = 'calc(100% + 375px)';
	  textnode.style.right = 'calc(100% + 375px)';
    }, 4300);
    window.setTimeout(function(){
      img.parentNode.removeChild(img);
	  textnode.parentNode.removeChild(textnode);
    }, 7300);

  };

var word = [
    "今天天气真不错","好伤心的一天","大兄der吃了没","wow 傻乎乎的你在干吗", "兄弟别来无恙！",
    "君不见，黄河之水天上来，奔流到海不复回。",
    "君不见，高堂明镜悲白发，朝如青丝暮成雪。",
    "人生得意须尽欢，莫使金樽空对月。",
    "天生我材必有用，千金散尽还复来。",
    "烹羊宰牛且为乐，会须一饮三百杯。",
    "岑夫子，丹丘生，将进酒，杯莫停。",
    "与君歌一曲，请君为我倾耳听。(倾耳听 一作：侧耳听)",
    "钟鼓馔玉不足贵，但愿长醉不愿醒。(不足贵 一作：何足贵；不愿醒 一作：不复醒)",
    "古来圣贤皆寂寞，惟有饮者留其名。(古来 一作：自古；惟 通：唯)",
    "陈王昔时宴平乐，斗酒十千恣欢谑。",
    "主人何为言少钱，径须沽取对君酌。",
    "五花马，千金裘，呼儿将出换美酒，与尔同销万古愁。",
    "噫吁嚱，危乎高哉！",
    "蜀道之难，难于上青天！",
    "蚕丛及鱼凫，开国何茫然！",
    "尔来四万八千岁，不与秦塞通人烟。",
    "西当太白有鸟道，可以横绝峨眉巅。",
    "地崩山摧壮士死，然后天梯石栈相钩连。",
    "上有六龙回日之高标，下有冲波逆折之回川。",
    "黄鹤之飞尚不得过，猿猱欲度愁攀援。(攀援 一作：攀缘)",
    "青泥何盘盘，百步九折萦岩峦。",
    "扪参历井仰胁息，以手抚膺坐长叹。",
    "问君西游何时还？畏途巉岩不可攀。",
    "但见悲鸟号古木，雄飞雌从绕林间。",
    "又闻子规啼夜月，愁空山。",
    "蜀道之难，难于上青天，使人听此凋朱颜！",
    "连峰去天不盈尺，枯松倒挂倚绝壁。",
    "飞湍瀑流争喧豗，砯崖转石万壑雷。",
    "其险也如此，嗟尔远道之人胡为乎来哉！(也如此 一作：也若此)",
    "剑阁峥嵘而崔嵬，一夫当关，万夫莫开。",
    "所守或匪亲，化为狼与豺。",
    "朝避猛虎，夕避长蛇；磨牙吮血，杀人如麻。",
    "锦城虽云乐，不如早还家。",
    "蜀道之难，难于上青天，侧身西望长咨嗟！"
];
//var func = [hi,penguin,lol,fly]
//var funcimg = ["./hi.gif","./penguin.gif","./lol.gif","./fly.gif"]
var func = [hi,lol];
var funcimg = ["https://cdn.mongona.com/static/img/penguin.gif","https://cdn.mongona.com/static/img/hi.gif"];
var l = word.length - 1;
var fl = func.length - 1;

function happy(){
	var i = parseInt(Math.round(Math.random()*l),10);
	var fi = parseInt(Math.round(Math.random()*fl),10);
	var w =word[i];
	var data = funcimg[fi];
	console.log(i,w,data);
	func[fi](data,w);
}


happy();
var t=6;
var num = Math.round(Math.random()*2+t);
window.setInterval(happy, 1000*num);