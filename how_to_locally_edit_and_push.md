open iterm
cd desktop / bdsp.... (on desktop)
jekyll serve (starts website)
http://localhost:4000/ (in chrome)

git diff
q

git add .
git commit -m "added cdac pig"
git push 


Remark:
you should always test your changes to make sure that they don't break anything. 
Be especially careful for small syntax issues, in, e.g., .yml files, which must obey strict syntax rules. 
In fact, it is **bad practice**, by which I mean inconveneint and error prone to rely on editing files with sensitive syntax. 
Unless you understand that syntax. 
Consider potentially writing a wrapper script that converts a file in easier format to the yml file.
But actually the yml format is pretty reasonable jsut dont' mes it up. 

Also, it is not very nice, and honestly likely not ery convenient either to have all your images on github. Furthermore, it greatly slows down all the operations like cloning the repo. 
It would be nicer to just make public links to the images from your dropbox or something and then just link those. 

Another note:
now when you run `jekyll serve` there will be a bunch of error messages. Just ignore them. They are not important. They are caused by SASS deciding to make a major breaking change and deprecating some syntax. But for whatever reason github was having a hard time @use'ing math, which is necessary to fix the division deprecation. Probably you could fix it, but this seems like not a pressing concern.