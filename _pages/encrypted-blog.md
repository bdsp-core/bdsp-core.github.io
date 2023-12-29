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
2eb1026e1a548548a022c7e5cabae15de36e33fe4befc2c4249302765d51712d61ee4b30a1f4a0d9183116c343fc95e3c71322d4d962163c4cabe27f41922d2df165db92ef9604b3967eaa66506fb0ec48aaf8ac619bee09712e0e7613c176a72d1368945030baa0e70562d97e150e255319049a1adf4019379e7fae96e662d431b37e1f257f0984b490a800cf1adb61a9b8aad9e461410985002c76c13013e8c43c2e733f23c45d90ba11e6f19cdf05b394faa9ec85ec6b7e200dc00404e6d84db354273b388bd3f922e079f5f4166ef5aae1dee63451032b3785f8fa08968012eef8a60ae25e4a2645b897bd5f60c1c871ad05e0f712a80141c84ea143bf113a821e62a88780c1933ef8dec4ba26e64b653e4a9305581e1b5cab9c8676d4a5259d38caf2f863d1b3902d5a323834bc3279f530e8172b4ef5f9a13f2db9808ec19cd71d8231eafc6588c20caa821a90c46658c7768340c4fd5ca36fa4f2369e69f027b8fcebd60627640ac85fa8b45f8cb42e146b9bc42fc5decf87f0747058da6211360b3459a57eb259c2029cacc577722c2b9938b5d1f2e8ab44d1d0de99c8ddab4b238a01e4744871dd37c10cde89f7dc0fab3264508e106456ea950ce4505ad848114497086a2f0003673c86b83b69cf4e78333510602692991d5df1ab5358f97f7d13d2170561a80083062013f4cdac3b2aee25aaf510f92f86acf3aa762a0012425757ade60d5a957f8bf065125d33ad342839385ee54b038ecbac8e16579104c0adb65c866b3b54e5615c5dbaf70bcee2555d4142c8fadcf6ca052a81666567a83dae505401f92ab87f57ad5fc94e0aa6c98c93f35dc370ec173eb3e91da95cd021d3fae93bf53d9c28e592d692011a03b71b09456660ddf3a55fbed1ccd8da47b737bc599f47bc4932e2bfdb16a28c6f682b4145dfee8506c945c6c17189e50c0176b9a60bc01157dfea3ec7554a947cc08dd7e27b631c81f2e1d74cad5396ed5baaf72c2f8706f7786be8d756e14595abbc478a591cd21aead69fec5fef151a0b34373c11e74da0cc2790b4aea220c89c80db89c687934db4efcc9ec7b7e9f3098bc4cbfd7a1458232eec81ec96036a4c3193158d3f63b282b8e7656293a73f7255fa957966590edd2b05826bba126cce112446d914550659f8ca8f35aec3fd56d5574d01572a2c92cac9ccc2faed66f18d71dfda18c98aa360dc38d4386d5c93f425998a3c021c1edf4b5153c8eb1ce5c9f845612513985740ff9b198eb168de9a40c5445df61b93e46d893f0d960fb2bab505b6c8427672b688f530db69919d85223dc9ae9bcae582047538e6d0e9daa5ce61f2c87176e61cd797eacf191ced79be5471fd542c65bd1b2773e434b2dc1f832737fb8af6941beed4132d17266ffa2c396590aaa1f9e222a82a2eb082bfe3fd1ba3f7ba1e2a75e54dedea02f6c77cd9e57e101266146bb22974c0bde9e23dc451543b5bbe839037b47368027de64296dc07a808401413a5dedd86ec713450536163e61e6c31b6907e74a1fea180482e8a0bdb06dba456c560a41bfdd8475cf2465f0d14205f571b82aa321131990bbaf2a112fa2eb98ec093fa2d7acbc73e49afd00c83b27855fbe4f1ceff73436a88bca13ca461298572c5281f1ee89995c438e7a2aa7d3a3323cc4bd472c9bd5eb4cd2f5554cb0f60bf8ace4da6c737a6f3c49a2c44d13d9db6171fe5ed76d28f0cbdc0d4aed8411593b84d5a56b2ba828a9ca133172567815180f3ae9a13fac3c2cd0112323a12218aab860ef63e3a359d94a00c410ac1af2375616195d52b2c5cf65ff8074ae67aa9ea9a8297b658aee00472df5d31d98cbf502b0c5e95096834e06088f6fbebe6bcb839ed8972cc3d4a7b668f340133a784df063f3f1caa98dafb7d4b4926a85049f33de020316bdf4f3326f93e29e22ea6667da13d9de7b713fc95bcd60b60ce08247b96b90fbaf3bb56c845043577e5baa9ba47f75d9b95de0c69a117cb9ab67765de92ce6e6b57aecd8772c6357df54590a7f9e3e45d445d9a49aabe7cd05e04f0be53a38dea93025fe1ce06ddb11363877bec4dc6f2ba55a550748a73afd64bebb7011201ca9cab43e1dec8a12e7897516a4590aa8d6952272f85cda3d8598bfd35fb0dc494d8d5a0e0be84311512bb7e42f54ea0a5f70ce7916162f2cc4abf262bc764a673d35d36b19d6d525c491986009a3403758e3df5df151c5bbfd1e5c2efc6915a938247cda6c0bbd37ce53a6a6148b34c401c1d0ba1c8696cf572b96e889be36e3a4819824424237d5ec910cf7a4a273fab1e4b00f174955cb6c2cc32758f72b644911d4012cea695e7c7c4d1dc3628e59dbf43d20f4edcc87e5c6eaf6129bd9bb36f8a0cc0ea9e25085d98d746ebe6378a5cf2e88063ddafc51d01d9565afe09c3ecec71d37f27659ed536064140fe5d6f2cb21221683177c0727e72f2b41334ae466ae592a729e4df4db6d41ae5227ca6288932f85cffb6df09a86961a3f3a55d2792688d5860eabfd9f6173fed58ff5c9f0b80d9d1f522de31e8ebdaa34727798eadbe93f6d3d2d69bf7216f07f557b9f36bb7ff47e422a74e5d066d15970d72b8e8a680c36d61149b8554cc214e431083c8e674f609fd6a883d1fde035a1f73982b84e02323c52183b3138e22f79657059b32a993f5bc5e3edf40aac784cc84d4904be3e38957f43fcb73442fd41d9986099969d9f47eb220d64c18cc13729e78da39a077da40b58b6d6af3c1575d31827b03921bcefd6822cf517fad08a78c1740bc37dc8098d0dbfb9156a9866c2840ba13722b305e2018ac419434d1ac4d67d923ead0e22b8036ba29dd5afca6017647b7d9a58a96e1a67314b25722921d43d7f3028fd469a9200f1320dab65bece2f64299740bd8f4b4d6136a6ee2ef43f36a573086856bdd0ea317616539f59f4d11b1ea16a96cf9cfbb6145ff9d4ee8a7127bcf49766fa1eded15ab6974f66968eb69efc21c2cf8f01e3f524d39d91ae1ab89b85030781b7ddf885bf5aae6853202a9ae97ed6a71937500250386119514bf5b3a25b0e08d3aac2267a2af284493e8e673adc88fa975ed7ab3563fe0cb64c28cc226d256809d6d175eaa03a771dfdd07b56c6175e34363da1795e4970ad24300d45a3a9395799c881222aecc7f2e3eef6b8f7d95830cc27316128942d8f122f8724437f19fbe0e2954552d0a44401ac0a5912095f84c7653ccc3df9d5c4828fc3bfa2fd49edf42fbade6a010f37a7eaa9191018c9e3f358741d9b4ab6640490d9c2cfd266d11d0c715ad6141cd8e1fe861be1dbe839769cc90a05a301ca1ec0a22a3f49d61dc1152168aa8cb17fe0c4bd825afa1b5ac37d89849a1d4816ec3332096e54d95a6294e6aca450720c4bb85cc98c8299bb88d09a6e1f5371b52534c2a34d8fc7f65490de1ca038b5c194ce1d582ca71136f02fa487e0b20f4528c1aa31469aaf55d6c827812e9e61d1781a8924fc4da9984793ca3c0b5b00139546ab0771e9d378b82a4d01391fb7bd3ab82a3c8e9a25c06d26d5269153e487bd3013d5e116484072aa09cb562744cc4485e19aec8daee8199cd83b58aa4f36351e1ded40cf5fb7106354141cb76d6439ab4a63bd84e750575b98814e81274192355d1025ae5474218316bac4e60a5a7f7e6ce933f62775dfb739fab1531d9cb06c85edef2f6a497358a26b1d8f19c0204157673d1fdd6b1cf47b6678d725ac1756f96f01bc4fcc09cc95ac81e43e1eb0643ce6af2535b1bab5e101a7932c17893c68ba3b8a09a3ea872f0ce5da8f885b10ced6a8dcfe3019e89357ba1758407aabbd903d7242c5bd91498e0325dc2cbfc7029b958f717552c6aebe6af1a089d37ace889bec1a5c199bdd2234316a681c6e1e0eff859d04625db0b029d4bfb2537806802cfaeb53ff90c7642fc6430b5e3be4ce069a74596f98514b8e6781c83f5012ea19f334b691f69971388bec14aa3ce6997b837d7e9961897a83ed349fb303f2461a1fb6334e6f5ad377141e8902eadd4f55e3c67e072441f1e007bf6b98239e9f3c8eee3196321592f1fe41652d812fa4afefc9d89fc36c13c4070db10cf807af7a4c6c59ae921af1148597192711722f710eeff5ed5d31dfb1654deffa8f97c3e1f0cc57ee596f0943a2a56e3235fbb5a969c787204e5606a01f7ade32209607a6aa18c90b67647a1493a8c1c4d3cfb854272a9b5b6e1c912070e767c62f7be1d522f3f7dbda70a2a29c92c91feb10231e65e1ec53c90e24118dd8493f14d558503ed61254a7c9f38e35c68fdddd1481745f13d0427f7c1830755dece23414e2224bce27cf0a11691f82d165a53f67d2be684886cd734466de0beea93c7c498fe4adc43d54fe4c7dbfe12907a2fb5686f0b8753013eafb78243ebb94beaa464d9069ad48efaae6408a909c1953adf81ca53dac526f4b7f3ca82ddee05d96b8ac58b9b073134638ae256316d207c37a0d36c4dd56510e428081f812902459e9f8b1c66d51f171e9623f3fc37ce5a79663e803e3cbc06061324d5883b239478bc767605208944f9d4c742750193d311435a6ec9cab6465ab4ad77e4f08dc1d79e3c57edbb9d921648bed2122ffe9bc46fac765a60c17918141b4aa46ed8063b68ac00c9d77da738a90ebdc7722afa80cacfcf736f7fb5123c9ffbae2937312a821acef06b197b70defcd463a9e64c141bd6e31d9fab6d8fce241b7e5b91ef7ec5d0023070b1eabe4051ca26283c81e93b03105bca5bbb85f8cbfa2dec404cf63e3bcc10ef153dbf42961773f7f0a81b44871af90fe91e747335b2aafbb3e38f2276a9636d32abcd5ef09cda84ac6850114aa25175dae3a1091780d8fc7d64f639e35c6ba50d8b8866f926b3f69df20e287c6a03fcae86cdc3668d3ad9eccde5f9802ba12974bbbc99444f844f1f882444e9f71218a9701a6425649d9e308867029f05d37c19691f37a849a7b2750a2e39e579a589f394b3fba5cec8edc05f0a9a0ab331448393434dd0f4a0003056fec829fa53f1f5fd545e215ba59a6f6d1c114a75d2bf4d002ff333d6d505f6bc318c6ff89ed501de5e60ec40b14b69b215ccc02f034b6d2b7e8eac8c3250caaca9f2ad0dd532cad89e183865e111a59f10f6951b94a2df2fb7d817907c366e83124bf846ce1d2d04594a6401a0c8ae1027b0da27750a6805b87349b42e74df29622c20fe0981e552d606f3aeb2ab6029825b85fd1aecfe533e72672f3d87d15bbe6c3b2741e4bd17c032f1d357f22c4cf1d0c631a74797e177f6402f2caa69f14184e2754f7a20057a70dea0652dc609e4ddca0f0fb9beed6cee540fa9ac9215e780168aa5b8ecf601a70e4c0ab712f3162ff57ce08e69ec46e082614b3c30d5cd17f93da794a0b86e64fcae7de10e92c32e04307fb994667471cf13e976ce0d90554f072a14d7b8dc8841c81c745e4c4d87dc7d861e6746c8c80d53034bd9b61a955e35413ade86916dc5da5639edd14aa5f767c8b12e832cba306439e6b0042df487fe3fa3bf329d872d7acfbbd05a69c7253e1c8bb384e1e548a4900609646503af3c4a81e43a8b83824bd4a2fb0174da5f88222247cc1b27607531c172c9081407dd4affe939091073fa0f48799b2213f23decc665d2040e8826d3afa80769dd09826d097ff7d5780509e1ab31aa3cd86b9b59cec758b81d9ef1ca34c8bdd4dfda6c2608e34b965331f421eb9c60186386a2f1e541c36de93efa3bedf4583d5c8030ad8f918fe7119ffc58c0fc5934c51f44bf975ebab91c3168334ab8277ec0f1f0ba6ccdf827b4b985aa53cbb067d7024ef1510b0b34c903f5caf03147993bf461014bbaa8e11f0e2a4d0c174d0a70377f94dce55e19f985e7c763bc5d1b21ce9e9aedac95ab277443dd6ac688f50b95241e06e266a4d60fb36cf5dac8fc729b51e992e83d677073297044ef7f42b0760c2316e973f27ebe1402dac7c6febbfe6088cd25ed14114a18bcc21374e00f609ce60da1e391afe0b29e1792c569ee184d2cc1403740541dbe856c1510cac0ee08b32dcc6560a68d1e2689b6b024ffe77fe2d400e877653ed3ff958ea8bf97d246be3f3abb86d6c975d11b22a5d5ab87a79eef7c9431bc6cb76cdbab18fe39add09593288bc01b3d0057c7e63b7c3d5477d5fec93c97fd57cc1056119e0f97b740b16ec320266c005eb5dfc2362d1568cfdb0ebafcbb9b7720eed9ab2f409e46a24200b19603c5e296bdfab079667890e24dd7767092fc5e3be60649f84ded0b70a2d42c50c93988c940d81392b4a20517ad7a02a2115ddcff0741f8de84f4adde81f38671131b7163a0e1638b5ba560406e0ab8680e426402268f39bfa121f5ea149fc807511af2ffc8c40ce882e951ef743a2cc93101c068dd767bdff3ab00ddcf66d7d38177f3a0296cb48afbad173229e3fff122724a22ca2ad873969b9c632c67a0baccbe82ea227c1f400580788f3bd7de1956d7f20f053e97b38d8e71246083c31b6f353e095107cb08cbbb6d4d9dd88de6018eb43901575d82b5b5a7eb5bb9524d80a4c00b84f48217f945e7b5aed7681c394c406da7a59a1cf259ef0d00235b229fbffa48e6b5c927963e8c940e642a7d08f91bbdfd50356ca0d723d0c26fa226eb07eda1cfcff295a90b50e2538d1442df2287ab7645e304a2e5bf43c5e2e01d447a5ddcb9ba0131a84bca73e82e26fe0bed08a11bf87305b45c842103286dc50072208bc7a275a8b9a287181eb1c7dd1391c0f93c37bd8cee4dd28a8b21dc3b954cf8a4ebb1240a8ff9f675c3c94e45a375c12e793573d307e6d9a31d61514053e6d61fb81585ee8872df5cb0f7cecccfc01c4c5ee1520f68fbb494da31bec8fd1e092f1341ca1063bd7051295d89236524c34f1611f73d8e171748cd95d2177fbb80418d7b87339c17f97e86262466a87a700a5ebf16b0e504801e33bb963b9e90a6fc821f23575077b72ff6d8a0b580addb707e917128fb21fd38fe9c024bd8c5eb6519ac52d957a5aabac78df1bffd2067fb113b67775843b2a794e2bf33290b966acd933ad5adc6473ee393ccbdfc3a9d51181c09a66ca93f358d69d38341a2eeae45b3c2aa8f499f9adaba8f3fd63cb7aa540c62028a924498417a33cb384ee9c3489d95f4e37d04e4fb44753fa276eb860c3591132b0a7f55ba180f9e9fe345206abb887d0274b4c1257bed1506c0d8616e3b4518c9c8f0ebecd74d14c6c61913f83edf1c4d397e5eedd9ad3266491c239ab96cee538ee1133af8d98843b73fce52d47006ec89aa07cddb1924b916f2674e873d3350aab9d63d5bebfeb334b997b3a2782dd64401b51b8d4ecb97bf1912f4eee0996c2324123185fc9cf769927d8586b5e0b75b530e3d2a52529a3614101bf5d8a146506aa72968068706f42292fb593a72fa9cdaad0cd35c55bf477154c42bb26995da13db2b70a57b3b2049fc643782586d92c5a43307f0da5b9d6467434621b835ffa4c861e8b73b8b8775841dee07b606971d5ae0726e25ddc0ec47c83311a3097035964e667714eb84c22bfebe8f5465f0a2f81e65831c55991ed1d0df2b47b8290d7760e0eb250d962126b9cb82ef08ce85193e4d7943b889f2f41dac8699996a206b0dd28ccb2e21a4f5e5338e4e921dd1dc434886a2630a084cfed8fc9156b1ece04dc29a4be60a6cf0497e8768ecf7d1b8d7187587ab46b7566c7132df7d2b8497393548da266a57659a56c722bda1553632f3cc98a03a704c6ab4ac761b6ed6d51dda42d9558e1901bc804f82d945d035a598179ac9338ae2738a2da372b16b28ea2d1fddc75f0ca52b5d7a5aff9514164636cd1d30a7d338a5e2543cf0cec3b0f1b9459d2133b98a20b0e80782c2cb858c368f1cf58fd1bbe5c0aa920d52a687759b03b1a92b3c6917cc8c3ec6b88f5ab84b834242b1779cffa5ff687f4ce020e624e9823711cb5ea0738ca8c553a673662c3fffdebafb7c936fb29832006df3cba6afed3f96f9ef67ccc99561cf8f085247e57c3ab7dab845221c07db04c839d7e521483d16b09bc56aba77aa75401316c13d8d16cc37397acabceea8e8ad48ca8ed499cedbec43aa79739fd9c64d3ab8ff7cec3dee5f5b326f7929c58fe2663688c9ae1de19e642529d035e75809830f864a0cb407c171e0f3aa148b34334bee99b2b4cb92d9845b5f26897025a17d1af694a22b946252ec15f7bce246fe322499975ff4ac85eb8fc2e830c7efd166440847e901f6670df2d9968fb2201c499328e44d06c7a6902773df10c42af948bcd760a14c5c533041f39aba672f9a6237bc8f73e1a84716df6187a928672cd4266df4b4bb87011991693a6beb7b9be396b1cdbe92ec02960a78eddebab30b86a25b6448be60bdbbd26727d9484afc76e74d028b3f8822a2b7f8c15f1882d480ce1b02c33498e4c49a35eee636fc3f87a4ef4b25
</div>
<div id="blog2">
Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.
Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.
Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.
Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.
Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.
Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.
Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.
Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.
Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.
Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.
Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.
Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.
Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.
Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.
Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.
Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.
Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.
Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.
</div>

<div id="blog3">
what ana amzing thrid blog post
</div>

<div id="birthday">
toda is my birthday i got a good birthday presetna nd ate a lot
toda is my birthday i got a good birthday presetna nd ate a lot
toda is my birthday i got a good birthday presetna nd ate a lot
toda is my birthday i got a good birthday presetna nd ate a lot
toda is my birthday i got a good birthday presetna nd ate a lot
toda is my birthday i got a good birthday presetna nd ate a lot
toda is my birthday i got a good birthday presetna nd ate a lot
toda is my birthday i got a good birthday presetna nd ate a lot
toda is my birthday i got a good birthday presetna nd ate a lot
**toda is my birthday i got a good birthday presetna nd ate a
lot**
of pizza. 
of pizza. 
of pizza. 
of pizza. 
of pizza. 
of pizza. 
of pizza. 
of pizza. 
of pizza. 
of pizza. 
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


