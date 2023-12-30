---
title: "ENC"
layout: textlay
excerpt: "ENC"
sitemap: false
permalink: /encrypted-blog/
---

<script src="https://cdnjs.cloudflare.com/ajax/libs/crypto-js/4.1.1/crypto-js.min.js"></script> <style>

div {
  word-wrap: break-word;
}
#blogtoc li {
    color: blue; /* Link-like blue color */
    text-decoration: underline; /* Underline like a link */
    cursor: pointer; /* Pointer cursor like a link */
}
#blogtoc li:hover {
    color: darkblue;
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

function decryptstuff(){
  let to_decrypt = $("#"+last_clicked_blog_post).text().trim();
  $("#"+last_clicked_blog_post).empty().append(DEC(to_decrypt));
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
  return decrypted;
}

/*
function appendText(text) {
      const displayDiv = document.getElementById("display");
      const newTextElement = document.createElement("p");
      newTextElement.textContent = text;

      const copyButton = document.createElement("button");
      copyButton.textContent = "Copy";
      copyButton.setAttribute("class", "copyBtn");
      copyButton.setAttribute("data-clipboard-text", text);

      const containerDiv = document.createElement("div");
      containerDiv.setAttribute("class", "containerDiv"); // Adding class for word-wrap
      containerDiv.appendChild(newTextElement);
      containerDiv.appendChild(copyButton);

      // Insert new elements at the beginning
      if (displayDiv.firstChild) {
        displayDiv.insertBefore(containerDiv, displayDiv.firstChild);
      } else {
        displayDiv.appendChild(containerDiv);
      }

      const divider = document.createElement("hr"); // Create divider element
      divider.setAttribute("class", "divider"); // Add class for styling
      displayDiv.insertBefore(divider, displayDiv.firstChild);
    }

// Initialize ClipboardJS
document.addEventListener('DOMContentLoaded', function() {
  new ClipboardJS('.copyBtn');
});
*/
</script>

<ul id="blogtoc">
<li>blog1</li>
<li>blog2</li>
<li>blog3</li>
<li>birthday</li>
<li>secret4</li>
</ul>

<div id="blog1">
0f2bf5260a981dbdecc57563f44bbf80d1fe85ee77f948bd369ed596f9e9f30cc5770684972fe5cd7f1501fd83d4fad5
</div>
<div id="blog2">
Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.
</div>

<div id="blog3">
what ana amzing thrid blog post
</div>

<div id="birthday">
toda is my birthday i got a good birthday presetna nd ate a lot
toda is my birthday i got a good birthday presetna nd ate a lot
toda is my birthday i got a good birthday presetna nd ate a lot
</div>

<div id="secret4">
79b4e2470bbb8c376129e58835e67e62d05956bfd646db5f34e040f625d70211aaef9c175b59c240025e94af75a3ebb65fb3bc3d348516bef8727e2c40fefdbddb79820196c6fae8daffe168591d7286c3d36575e4a166e7a50067c8f3dc75b66b460d0197ca439e1ca39b232c2e7aaa
</div>

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

-----
-----
-----
-----
-----
-----
-----
-----
-----
-----
-----
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
Here is some more filler text because the website looks bad if there is not enough text.


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


