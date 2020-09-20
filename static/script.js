// Navbar
// menu button 
const menuBtn = document.querySelector("#menu-btn")
const navItems = document.querySelector("#nav-items")
const nav = document.querySelector("nav")
const logoImg = document.querySelector("#logo-img")
const logoDiv = document.querySelector("#logo")
menuBtn.addEventListener('click',function(){
    navItems.classList.toggle('clicked');
    menuBtn.classList.toggle('rotate');
    
});
menuBtn.addEventListener('blur',function(){
        navItems.classList.remove('clicked');
        menuBtn.classList.toggle('rotate');
});

window.addEventListener("scroll",function(){
    navItems.classList.remove('clicked', scrollY > 111);
});

// navbar scroll

window.addEventListener("scroll", function(){
    nav.classList.toggle("scroll",scrollY > 30);
    logoImg.classList.toggle("scroll",scrollY > 30);
    logoDiv.classList.toggle("scroll",scrollY > 30);
});

const preloader = document.querySelector(".preloader");
window.addEventListener("load",function (){
    setTimeout( function(){
    preloader.classList.add("hidden");
    nav.classList.add("sticky-top");
},500)});



