#!/usr/bin/env python3
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs, quote
from http import cookies
from pathlib import Path
import sqlite3, hashlib, html, os, secrets

ROOT=Path(__file__).resolve().parent
DB=ROOT/'ctf.db'
CH=ROOT.parent
SESSION={}

def db():
    c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; return c

def h(v): return hashlib.sha256(v.encode()).hexdigest()

def init():
    c=db(); c.executescript('''
    CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, username TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
    CREATE TABLE IF NOT EXISTS challenges(id INTEGER PRIMARY KEY, slug TEXT UNIQUE, name TEXT, category TEXT, points INTEGER, description TEXT, kind TEXT, flag_hash TEXT, artifact TEXT, launch_url TEXT, enabled INTEGER DEFAULT 1);
    CREATE TABLE IF NOT EXISTS solves(user_id INTEGER, challenge_id INTEGER, solved_at TEXT DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY(user_id,challenge_id));
    ''')
    if c.execute('SELECT COUNT(*) FROM challenges').fetchone()[0]==0:
        rows=[
        ('ch1','The Forgotten Endpoint','Web',100,'Find the forgotten administrative endpoint disclosed by the web application.','live','SBB{robots_txt_never_lies}',None,'http://localhost:8080/'),
        ('ch2',"Pixels Don't Lie",'Forensics',100,"A suspicious image was pulled from the target's cloud backup. Something is hidden inside its pixels.",'file','SBB{pixels_never_lie_lsb_reveals_all}','ch2/suspicious_image.png',None),
        ('ch3','Cracked Seal','Cryptography',150,'Recover the plaintext by deriving the AES key from the narrow timestamp window.','file','SBB{time_based_keys_are_not_random}','ch3/message.enc|ch3/note.txt',None),
        ('ch4','Trace the Ghost','OSINT',150,'Intercepted infrastructure logs point to the handle n0mad_dev. Trace their public footprint - a repo and an old competition - to reconstruct the flag.','file','SBB{n0mad_leaves_footprints_in_commit_history}','ch4/starting_clue.txt|ch4/event_page/index.html|ch4/n0mad_dev-portfolio.zip',None),
        ('ch5','The Silent Capture','Forensics',200,'Analyze the network capture and correlate the two artifacts to recover the flag.','file','SBB{halfway_through_the_wire_and_found_in_headers}','ch5/capture.pcapng',None),
        ('ch6','Break the Lock (Capstone)','Reverse Engineering / Linux',200,"Two-part capstone. Part A (download below): reverse-engineer the lock binary to recover an access credential. Part B (live): once the organizer starts the container (cd challenges/ch6/partB && CH6_PLAYER_PASSWORD=<credential> CH6_FLAG=... ./build.sh), SSH in as player@localhost -p 2222 using the credential from Part A, then find and exploit an overly broad sudo rule to read root's flag. Only the Part B flag is scored.",'file','SBB{sudo_wildcard_is_not_a_sandbox}','ch6/partA/lock|ch6/partA/README.txt',None)]
        for slug,name,cat,pts,desc,kind,flag,artifact,url in rows:
            c.execute('INSERT INTO challenges(slug,name,category,points,description,kind,flag_hash,artifact,launch_url) VALUES(?,?,?,?,?,?,?,?,?)',(slug,name,cat,pts,desc,kind,h(flag) if flag else None,artifact,url))
    c.commit(); c.close()

def page(title,body,user=None):
    nav='<a href="/">Dashboard</a><a href="/challenges">Challenges</a><a href="/scoreboard">Scoreboard</a>'
    if user: nav+=f'<span class="user">{html.escape(user)}</span><a href="/logout">Logout</a>'
    else: nav+='<a href="/login">Login</a><a href="/register">Register</a>'
    return '<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+html.escape(title)+' — SentinelBreach</title><link rel="stylesheet" href="/static/style.css"></head><body><header><div class="brand">SENTINEL<span>BREACH</span></div><nav>'+nav+'</nav></header><main>'+body+'</main><footer>SentinelBreach • Operation Blackwire</footer></body></html>'

def form_page(title,action,msg=''):
    body='<section class="card narrow"><h1>'+html.escape(title)+'</h1>'
    if msg: body+='<div class="msg">'+html.escape(msg)+'</div>'
    body+='<form method="post" action="'+action+'"><label>Username<input name="username" required></label><label>Password<input name="password" type="password" required></label><button>Submit</button></form></section>'
    return page(title,body)

class H(BaseHTTPRequestHandler):
    def user(self):
        sid=self.cookies().get('sid'); return SESSION.get(sid.value) if sid else None
    def cookies(self):
        c=cookies.SimpleCookie(); c.load(self.headers.get('Cookie','')); return c
    def send(self,status=200,ctype='text/html; charset=utf-8',body=b''):
        if isinstance(body, str):
            body=body.encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type',ctype)
        self.send_header('Content-Length',str(len(body)))
        self.end_headers()
        self.wfile.write(body)
    def redirect(self,path): self.send_response(303); self.send_header('Location',path); self.end_headers()
    def body(self):
        n=int(self.headers.get('Content-Length','0')); return parse_qs(self.rfile.read(n).decode())
    def do_GET(self):
        path=urlparse(self.path).path; user=self.user()
        if path=='/static/style.css': return self.send(200,'text/css; charset=utf-8',(ROOT/'static/style.css').read_bytes())
        if path=='/login': return self.send(body=form_page('Login','/login'))
        if path=='/register': return self.send(body=form_page('Create account','/register'))
        if path=='/logout':
            sid=self.cookies().get('sid')
            if sid: SESSION.pop(sid.value,None)
            return self.redirect('/login')
        if not user: return self.redirect('/login')
        c=db()
        if path in ('/','/challenges'):
            rows=c.execute('SELECT * FROM challenges WHERE enabled=1 ORDER BY id').fetchall(); uid=c.execute('SELECT id FROM users WHERE username=?',(user,)).fetchone()['id']; solved={x['challenge_id'] for x in c.execute('SELECT challenge_id FROM solves WHERE user_id=?',(uid,))}; c.close()
            cards=''.join('<article class="challenge"><div class="tag">'+html.escape(r['category'])+'</div><h2>CH'+str(r['id'])+' — '+html.escape(r['name'])+'</h2><p>'+html.escape(r['description'])+'</p><div class="meta">'+str(r['points'])+' points · '+('SOLVED' if r['id'] in solved else 'UNSOLVED')+'</div><a class="button" href="/challenge/'+r['slug']+'">Open</a></article>' for r in rows)
            return self.send(body=page('Dashboard','<section class="hero"><p class="eyebrow">OPERATION BLACKWIRE</p><h1>CTF Challenge Portal</h1><p>Six challenge slots, one scoreboard. CH1, CH3 and CH5 are integrated now; CH2, CH4 and CH6 are ready for your teammate.</p></section><div class="grid">'+cards+'</div>',user))
        if path.startswith('/challenge/'):
            slug=path.split('/',2)[2]; r=c.execute('SELECT * FROM challenges WHERE slug=?',(slug,)).fetchone(); uid=c.execute('SELECT id FROM users WHERE username=?',(user,)).fetchone()['id']
            if not r: c.close(); return self.send(404,body=b'Not found')
            solved=bool(c.execute('SELECT 1 FROM solves WHERE user_id=? AND challenge_id=?',(uid,r['id'])).fetchone()); c.close(); extra=''
            if r['kind']=='file':
                for item in r['artifact'].split('|'): extra+='<a class="download" href="/download/'+quote(item,safe='/')+'">Download '+html.escape(Path(item).name)+'</a>'
            elif r['kind']=='live': extra='<a class="button" href="'+html.escape(r['launch_url'])+'" target="_blank">Launch challenge</a><p class="hint">This challenge runs separately from the portal. Return here to submit the discovered flag.</p>'
            else: extra='<div class="placeholder">Waiting for teammate challenge files.</div>'
            submit='' if solved or r['kind']=='placeholder' else '<form method="post" action="/submit/'+r['slug']+'" class="flagform"><input name="flag" placeholder="SBB{...}" required><button>Submit Flag</button></form>'
            status='<div class="solved">✓ Solved</div>' if solved else ''
            body='<section class="card"><div class="tag">CH'+str(r['id'])+' · '+html.escape(r['category'])+' · '+str(r['points'])+' pts</div><h1>'+html.escape(r['name'])+'</h1><p class="lead">'+html.escape(r['description'])+'</p>'+extra+submit+status+'</section>'
            return self.send(body=page(r['name'],body,user))
        if path.startswith('/download/'):
            rel=path[len('/download/'):].lstrip('/')
            # Only allow artifacts explicitly assigned to enabled file challenges.
            allowed=False
            for rr in c.execute("SELECT artifact FROM challenges WHERE enabled=1 AND kind='file' AND artifact IS NOT NULL").fetchall():
                if rel in rr['artifact'].split('|'):
                    allowed=True
                    break
            if not allowed or '..' in Path(rel).parts:
                c.close(); return self.send(404,body=b'Not found')
            target=(CH/rel).resolve()
            base=CH.resolve()
            if base not in target.parents or not target.is_file():
                c.close(); return self.send(404,body=b'Not found')
            c.close()
            ctype='text/plain; charset=utf-8' if target.suffix=='.txt' else 'application/octet-stream'
            return self.send(200,ctype,target.read_bytes())
        if path=='/scoreboard':
            rows=c.execute('SELECT u.username,COALESCE(SUM(ch.points),0) points,COUNT(s.challenge_id) solves FROM users u LEFT JOIN solves s ON u.id=s.user_id LEFT JOIN challenges ch ON ch.id=s.challenge_id GROUP BY u.id ORDER BY points DESC,solves DESC,u.username').fetchall(); c.close(); table=''.join(f'<tr><td>{i}</td><td>{html.escape(r["username"])}</td><td>{r["solves"]}</td><td>{r["points"]}</td></tr>' for i,r in enumerate(rows,1)); return self.send(body=page('Scoreboard','<section class="card"><h1>Scoreboard</h1><table><tr><th>#</th><th>Player</th><th>Solves</th><th>Points</th></tr>'+table+'</table></section>',user))
        c.close(); return self.send(404,body=b'Not found')
    def do_POST(self):
        path=urlparse(self.path).path; data=self.body()
        if path in ('/login','/register'):
            u=data.get('username',[''])[0].strip(); pw=data.get('password',[''])[0]; c=db()
            if not u or not pw: c.close(); return self.send(body=form_page('Login' if path=='/login' else 'Create account',path,'Fill in both fields.'))
            try:
                if path=='/register': c.execute('INSERT INTO users(username,password_hash) VALUES(?,?)',(u,h(pw))); c.commit()
                row=c.execute('SELECT id FROM users WHERE username=? AND password_hash=?',(u,h(pw))).fetchone()
            except sqlite3.IntegrityError: c.close(); return self.send(body=form_page('Create account','/register','Username already exists.'))
            c.close()
            if row:
                sid=secrets.token_urlsafe(24); SESSION[sid]=u; self.send_response(303); self.send_header('Location','/'); self.send_header('Set-Cookie',f'sid={sid}; HttpOnly; SameSite=Lax'); self.end_headers(); return
            return self.send(body=form_page('Login','/login','Invalid username or password.'))
        user=self.user()
        if not user: return self.redirect('/login')
        if path.startswith('/submit/'):
            slug=path.split('/',2)[2]; flag=data.get('flag',[''])[0].strip(); c=db(); r=c.execute('SELECT * FROM challenges WHERE slug=?',(slug,)).fetchone(); uid=c.execute('SELECT id FROM users WHERE username=?',(user,)).fetchone()['id']
            if not r: c.close(); return self.send(404,body=b'Not found')
            already=c.execute('SELECT 1 FROM solves WHERE user_id=? AND challenge_id=?',(uid,r['id'])).fetchone()
            if not already and r['flag_hash'] and h(flag)==r['flag_hash']:
                c.execute('INSERT INTO solves(user_id,challenge_id) VALUES(?,?)',(uid,r['id'])); c.commit(); c.close(); return self.redirect('/challenge/'+slug)
            c.close(); return self.send(body=page(r['name'],'<section class="card"><h1>Incorrect flag</h1><p>The submitted flag was not accepted.</p><a class="button" href="/challenge/'+slug+'">Back</a></section>',user))
        return self.send(404,body=b'Not found')

def main():
    init(); port=int(os.environ.get('PORT','8000')); print(f'SentinelBreach: http://localhost:{port}'); ThreadingHTTPServer(('0.0.0.0',port),H).serve_forever()
if __name__=='__main__': main()
