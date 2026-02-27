import subprocess, pathlib
repo=pathlib.Path(r'c:/Repos/Theory of Everything')
res=subprocess.run(['py','-3',str(repo/'tools'/'duad_we6_conjugacy.py')],cwd=str(repo),capture_output=True,text=True)
print('rc',res.returncode)
print('stdout')
print(res.stdout)
print('stderr')
print(res.stderr)
