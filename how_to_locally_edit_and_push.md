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