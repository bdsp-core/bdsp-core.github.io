---
title: "ENC"
layout: textlay
excerpt: "ENC"
sitemap: false
permalink: /encrypted-blog-alek/
---

<script src="https://cdnjs.cloudflare.com/ajax/libs/crypto-js/4.1.1/crypto-js.min.js"></script> <style>

#main-content {
  margin-left: 200px;
  padding: 20px;
}

#toc {
  position: fixed;
  width: 200px;
  max-height: 50vh; /* or any specific height you prefer */
  overflow-y: auto; /* this enables scrolling */
  background-color: #000000; /* Black background */
  color: #ffffff; /* White text */
}


div {
  word-wrap: break-word;
}

#blogtoc li {
    color: ghostwhite; /* Link-like blue color */
    cursor: pointer; /* Pointer cursor like a link */
}
#blogtoc li:hover {
    color: red;
}

#toc {
  float: right;
  width: 200px; /* adjust width as needed */
}

/* this is kind of a hack, but I think it's a workable solution */
blockquote {
    padding: 5px 20px;
    margin: 0 0 20px;
    font-size: 16px;
    border-left: 5px solid #eee;
    #background-color: red;
}
blockquote strong em {
  color: #7F8C8D;
}


</style>

<button onclick="decryptstuff()">decrypt encrypted blog post</button>
<label for="password">Password:</label>
<input id="password" type="password" style="width: 50%;">


<script>
const iv = CryptoJS.enc.Hex.parse('6ed541b6ca008267aec855b643fe4dfc');
let last_clicked_blog_post = "blog1";

// function decryptstuff(){
//   let to_decrypt = $("#"+last_clicked_blog_post).text().trim();
//   $("#"+last_clicked_blog_post).empty().append(DEC(to_decrypt));
// }

function decryptstuff(){
  let ciphertextHex = $("#"+last_clicked_blog_post).text().trim(); // Get the encrypted text as hexadecimal string
  let decryptedText = DEC(ciphertextHex); // Decrypt the text
  $("#"+last_clicked_blog_post).empty().append(decryptedText); // Display the decrypted text
}

function getPassword(){
  return document.getElementById("password").value;
}

function clickEnc(){
  let plaintext = document.getElementById("inputtext").value;
  console.log(plaintext);
  console.log(ENC(plaintext));
  appendText(ENC(plaintext));
}
function clickDec(){
  let ciphertext = document.getElementById("inputtext").value;
  console.log(ciphertext);
  console.log(DEC(ciphertext));
  appendText(DEC(ciphertext));
}

function ENC(plaintext){
  const key = CryptoJS.PBKDF2(getPassword(), '', { keySize: 192 / 32, iterations: 10000 });
  const encrypted = CryptoJS.AES.encrypt(plaintext, key, { iv: iv, mode: CryptoJS.mode.CBC, padding: CryptoJS.pad.Pkcs7 });
  const encryptedHex = encrypted.ciphertext.toString(CryptoJS.enc.Hex);
  return encryptedHex;
}

function DEC(ciphertext){
  const key = CryptoJS.PBKDF2(getPassword(), '', { keySize: 192 / 32, iterations: 10000 });
  const encryptedCiphertext = CryptoJS.enc.Hex.parse(ciphertext);
  const decrypted = CryptoJS.AES.decrypt(
    { ciphertext: encryptedCiphertext },
    key,
    { iv: iv, mode: CryptoJS.mode.CBC, padding: CryptoJS.pad.Pkcs7 }
  ).toString(CryptoJS.enc.Utf8);
  return decrypted.replace(/\n/g, '<br>');
}

</script>


<div id='toc'>
<ul id='blogtoc'>
</ul>
</div>
<div id='main-content'></div>

<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<!-- TEMPLATE REPLACE TEXT DO NOT DELETE  -->
-----
-----
-----
-----
-----
-----
-----
-----
-----

Click on a blog post in the table of contents to view the
contents of the blog post.

<script>
let blog_post_names = [];
document.addEventListener('DOMContentLoaded', () => {
    const listItems = document.querySelectorAll('#blogtoc li');
    listItems.forEach(item => {
        blog_post_names.push(item.textContent);
        $("#"+item.textContent).hide();

        item.addEventListener('click', function() {
            const currentBlogPost = this.textContent;
            last_clicked_blog_post = currentBlogPost;
            for (const blog_name of blog_post_names){
              if (blog_name == currentBlogPost){
                $("#"+blog_name).show();
              }
              else {
                $("#"+blog_name).hide();
              }
            }

        });
    });
});
</script>