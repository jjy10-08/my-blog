//main_page中滑动图片　　新建一个数组保存全部图片的地址
var arrImgs=['imgs/pic01.jpg','imgs/pic02.jpg','imgs/pic03.jpg','imgs/pic04.jpg','imgs/pic05.jpg']
//获取右侧单击按钮对象
var rright=document.getElementsByClassName('rright')[0];
//获取左侧单击按钮对象
var lleft=document.getElementsByClassName('lleft')[0];
//获取显示图片元素对象
var img=document.getElementById('img')
//定义一个下标变量
var index=0
//绑定右侧按钮点击事件
rright.onclick=function () {
    //下标累加１
    index++;
    //判断是否超过最大值
    if (index==arrImgs.length) index=0;
    //调用需改属性方法重置图片对象的来源
    img.setAttribute('src',arrImgs[index]);
}
//绑定左侧按钮点击事件
lleft.onclick=function () {
    //判断是否小于０
    if (index==0) index=arrImgs.length;
    //下标累减
    index--;
    img.setAttribute('src',arrImgs[index]);
}
  