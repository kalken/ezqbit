# Mock qBittorrent backend for trying the theme without a real qBittorrent: serves a built
# WebUI folder with canned API data (nine torrents, categories, tags, trackers, a log).
#
# Usage:
#   ./build.sh 5.2.4 /tmp/ezqbit-webui
#   python3 dev/mock_server.py /tmp/ezqbit-webui 18099
#   open "http://localhost:18099/?scheme=dark"        (or scheme=light; /login for the login page)
#
# css/ezqbit.css and css/ezqbit-login.css are served straight from this repository, so an
# edit shows up on a browser refresh without rebuilding.
#
# Add &demo=<name> to open a dialog or view after loading, e.g. ?scheme=dark&demo=prefs.
# The names are the keys of ACTIONS below.
import json, re, sys, os, time, hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs
ROOT = sys.argv[1]; PORT = int(sys.argv[2])
THEME = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "css")
TR = re.compile(r"QBT_TR\((.*?)\)QBT_TR\[CONTEXT=[^\]]*\]", re.S)
TYPES = {".html":"text/html", ".js":"text/javascript", ".css":"text/css", ".svg":"image/svg+xml", ".png":"image/png", ".txt":"text/plain"}
now = int(time.time())
GiB = 1024**3; MiB = 1024**2
def T(name, size, prog, state, cat, tags, tracker, dl=0, up=0, seeds=(0,0), peers=(0,0), prio=0, ratio=0.0):
    return dict(name=name, size=size, total_size=size, progress=prog, state=state, category=cat, tags=tags, tracker=tracker,
        dlspeed=dl, upspeed=up, num_seeds=seeds[0], num_complete=seeds[1], num_leechs=peers[0], num_incomplete=peers[1],
        priority=prio, ratio=ratio, popularity=ratio/2, eta=8640000 if not dl else int(size*(1-prog)/dl), added_on=now-86400*3,
        completion_on=(now-3600 if prog==1 else -1), amount_left=int(size*(1-prog)), completed=int(size*prog),
        downloaded=int(size*prog), uploaded=int(size*prog*ratio), downloaded_session=0, uploaded_session=0,
        dl_limit=0, up_limit=0, max_ratio=-1, max_seeding_time=-1, max_inactive_seeding_time=-1, ratio_limit=-2,
        seeding_time_limit=-2, inactive_seeding_time_limit=-2, seen_complete=now-600, last_activity=now-60,
        time_active=7200, seeding_time=0, save_path="/downloads", download_path="", content_path="/downloads/"+name,
        root_path="", availability=1.0 if prog<1 else -1, auto_tmm=False, force_start=False, super_seeding=False,
        seq_dl=False, f_l_piece_prio=False, private=False, has_metadata=True, reannounce=900, comment="",
        infohash_v1=hashlib.sha1(name.encode()).hexdigest(), infohash_v2="", magnet_uri="", trackers_count=1)
TK1="https://tracker.example.org/announce"; TK2="https://torrent.example.net/announce"
LIST = [
 T("ubuntu-24.04.1-desktop-amd64.iso", int(5.8*GiB), 0.431, "downloading", "Linux", "iso", TK1, dl=int(4.0*MiB), seeds=(18,412), peers=(3,10), prio=1),
 T("debian-12.7.0-amd64-DVD-1.iso", int(3.7*GiB), 0.0, "stoppedDL", "Linux", "iso", TK1, peers=(0,3), prio=2),
 T("Big Buck Bunny 4K", int(243.3*MiB), 0.061, "stoppedDL", "", "open-movies", TK2, peers=(0,3), prio=3),
 T("Sintel (2010) 1080p", int(1.81*GiB), 0.0, "stoppedDL", "", "open-movies", TK2, peers=(0,3), prio=4),
 T("archlinux-2026.10.01-x86_64.iso", int(1.15*GiB), 0.598, "stalledDL", "Linux", "iso", TK1, peers=(0,2), prio=5),
 T("Tears of Steel", int(784*MiB), 0.0, "queuedDL", "", "open-movies", TK2, peers=(0,3), prio=6),
 T("fedora-workstation-41.iso", int(2.27*GiB), 1.0, "stoppedUP", "Linux", "iso", TK1, peers=(0,5), ratio=1.2),
 T("Elephants Dream", int(488.5*MiB), 1.0, "uploading", "", "open-movies", TK2, up=int(312.5*1024), peers=(2,4), ratio=2.4),
 T("Cosmos Laundromat", int(592*MiB), 1.0, "stalledUP", "", "open-movies", TK2, peers=(0,4), ratio=0.8),
]
TORRENTS = {t["infohash_v1"]: t for t in LIST}
MAIN = dict(rid=1, full_update=True, torrents=TORRENTS,
    categories={"Linux": {"name":"Linux","savePath":""}, "Movies": {"name":"Movies","savePath":""}},
    tags=["iso","open-movies"],
    trackers={TK1:[h for h,t in TORRENTS.items() if t["tracker"]==TK1], TK2:[h for h,t in TORRENTS.items() if t["tracker"]==TK2]},
    server_state=dict(connection_status="connected", dht_nodes=216, dl_info_speed=int(4.0*MiB), dl_info_data=0, up_info_speed=int(312.5*1024),
        up_info_data=0, dl_rate_limit=0, up_rate_limit=0, free_space_on_disk=412*GiB, queueing=True, use_alt_speed_limits=False,
        refresh_interval=1500, use_subcategories=False, last_external_address_v4="203.0.113.42", last_external_address_v6="2001:db8::42",
        alltime_dl=0, alltime_ul=0, global_ratio="0", total_wasted_session=0, total_peer_connections=0, read_cache_hits="0",
        total_buffers_size=0, write_cache_overload="0", read_cache_overload="0", queued_io_jobs=0, average_time_queue=0, total_queued_size=0))
PREFS = dict(locale="en", status_bar_external_ip=True, dht=True, queueing_enabled=True, use_subcategories=False,
    web_ui_username="admin", refresh_interval=1500, confirm_torrent_deletion=True, alt_dl_limit=0, alt_up_limit=0, dl_limit=0, up_limit=0)
STATE = dict(scheme="dark", demo="")
ROW = "const row=document.querySelector('#torrentsTableDiv tbody tr');"
ACTIONS = dict(
    prefs="document.getElementById('preferencesButton').click()",
    about="document.getElementById('aboutLink').click()",
    stats="document.getElementById('StatisticsLink').click()",
    addlink="document.getElementById('downloadButton').click()",
    menu="document.querySelectorAll('#desktopNavbar > ul > li')[2].classList.add('ieHover')",
    navopen="document.getElementById('desktopNavbar').setAttribute('data-demo-open','');document.querySelectorAll('#desktopNavbar > ul > li')[2].classList.add('ieHover')",
    navbar="document.getElementById('desktopNavbar').setAttribute('data-demo-open','')",
    context=ROW+"for(const t of ['mousedown','mouseup','click'])row.dispatchEvent(new MouseEvent(t,{bubbles:true,clientX:400,clientY:145}));row.dispatchEvent(new MouseEvent('contextmenu',{bubbles:true,cancelable:true,clientX:400,clientY:145,button:2}))",
    trackers=ROW+"for(const t of ['mousedown','mouseup','click'])row.dispatchEvent(new MouseEvent(t,{bubbles:true,clientX:400,clientY:145}));document.getElementById('propTrackersLink').click()",
    general=ROW+"for(const t of ['mousedown','mouseup','click'])row.dispatchEvent(new MouseEvent(t,{bubbles:true,clientX:400,clientY:145}));",
    delete=ROW+"for(const t of ['mousedown','mouseup','click'])row.dispatchEvent(new MouseEvent(t,{bubbles:true,clientX:400,clientY:145}));document.getElementById('deleteButton').click()",
    search="document.getElementById('searchTabLink').click()",
    rss="document.getElementById('rssTabLink').click()",
    log="document.getElementById('logTabLink').click()",
    notoolbar="1",
    general2="1",
    creator="document.getElementById('torrentCreatorButton').click()",
)
class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def send(self, body, ctype="application/json", code=200):
        if not isinstance(body, bytes): body = body.encode()
        self.send_response(code); self.send_header("Content-Type", ctype); self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store"); self.end_headers(); self.wfile.write(body)
    def do_POST(self):
        n = int(self.headers.get("Content-Length") or 0); self.rfile.read(n); self.do_GET()
    def do_GET(self):
        path = urlparse(self.path).path
        if path.startswith("/api/v2/"):
            ep = path[8:]
            if ep == "app/version": return self.send("v5.2.4", "text/plain")
            if ep == "app/webapiVersion": return self.send("2.11.4", "text/plain")
            if ep == "app/preferences": return self.send(json.dumps(PREFS))
            if ep == "sync/maindata": return self.send(json.dumps(MAIN))
            if ep == "clientdata/load": return self.send(json.dumps({"qbt_color_scheme": STATE["scheme"], "qbt_show_log_viewer": STATE["demo"] != "readme", "qbt_show_top_toolbar": STATE["demo"] != "notoolbar"}))
            if ep == "torrents/trackers": return self.send(json.dumps([
                dict(url="** [DHT] **", status=2, tier=-1, num_peers=12, num_seeds=0, num_leeches=0, num_downloaded=0, msg="", next_announce=0, min_announce=0, endpoints=[]),
                dict(url=TK1, status=2, tier=0, num_peers=40, num_seeds=412, num_leeches=10, num_downloaded=9000, msg="", next_announce=now+900, min_announce=now+60, endpoints=[]),
                dict(url="https://backup.example.org/announce", status=4, tier=1, num_peers=0, num_seeds=0, num_leeches=0, num_downloaded=0, msg="timed out", next_announce=now+300, min_announce=now+60, endpoints=[])]))
            if ep == "torrents/properties": return self.send(json.dumps(dict(save_path="/downloads", creation_date=now-9e5, piece_size=4*MiB, comment="", total_wasted=0,
                total_uploaded=0, total_uploaded_session=0, total_downloaded=2*GiB, total_downloaded_session=2*GiB, up_limit=-1, dl_limit=-1, time_elapsed=7200, seeding_time=0,
                nb_connections=21, nb_connections_limit=100, share_ratio=0, addition_date=now-3e5, completion_date=-1, created_by="mktorrent", dl_speed_avg=3*MiB, dl_speed=4*MiB,
                eta=840, last_seen=now-600, peers=3, peers_total=10, pieces_have=640, pieces_num=1485, reannounce=900, seeds=18, seeds_total=412, total_size=int(5.8*GiB),
                up_speed_avg=0, up_speed=0, is_private=False, popularity=0, infohash_v1=LIST[0]["infohash_v1"], infohash_v2="", name=LIST[0]["name"], hash=LIST[0]["infohash_v1"])))
            if ep == "log/main": return self.send(json.dumps([dict(id=i, message=m, timestamp=now-600+i*30, type=t) for i,(m,t) in enumerate([
                ("qBittorrent v5.2.4 started", 1), ("Web UI: Now listening on IP: 127.0.0.1, port: 8080", 2), ("Successfully listening on IP. IP: 203.0.113.42. Port: TCP/6881", 2),
                ("Tracker timed out. Torrent: archlinux-2026.10.01-x86_64.iso", 4), ("Failed to load torrent. Reason: invalid bencoding", 8), ("Added new torrent. Torrent: ubuntu-24.04.1-desktop-amd64.iso", 2)])]))
            if ep == "search/plugins": return self.send(json.dumps([dict(name="demo", fullName="Demo engine", enabled=True, url="https://example.org", version="1.0",
                supportedCategories=[dict(id="all", name="All categories")])]))
            if ep == "rss/items": return self.send(json.dumps({"Linux releases": dict(uid="{1}", url="https://example.org/feed", title="Linux releases", lastBuildDate="", isLoading=False, hasError=False,
                articles=[dict(id=str(i), title=t, date="03 Oct 2026 12:00:00 +0000", link="https://example.org/"+str(i), torrentURL="https://example.org/"+str(i)+".torrent", isRead=(i>1), description="Release notes for "+t)
                          for i,t in enumerate(["Ubuntu 24.04.1 released", "Debian 12.7 released", "Fedora 41 released", "Arch Linux 2026.10.01"])])}))
            if ep == "rss/rules": return self.send("{}")
            if ep in ("torrents/webseeds","torrents/files","log/peers","app/networkInterfaceList","app/networkInterfaceAddressList","torrents/categories"): return self.send("[]")
            sys.stderr.write("API "+ep+"\n"); return self.send("{}")
        q = parse_qs(urlparse(self.path).query)
        if path == "/":
            path = "/index.html"; STATE["scheme"] = q.get("scheme", ["dark"])[0]; STATE["demo"] = q.get("demo", [""])[0]
        if path == "/login": path = "/public-index"
        for base in (("public","/index.html"),) if path == "/public-index" else (("private",path),("public",path)):
            f = os.path.join(ROOT, base[0], base[1].lstrip("/"))
            if path in ("/css/ezqbit.css", "/css/ezqbit-login.css"): f = os.path.join(THEME, path[5:])
            if os.path.isfile(f):
                ext = os.path.splitext(f)[1]; data = open(f,"rb").read()
                if ext in (".html",".js",".css"):
                    s = data.decode("utf-8"); s = TR.sub(lambda m: m.group(1), s).replace("${LANG}","en").replace("${CACHEID}","1")
                    if path == "/index.html" and STATE["demo"] in ACTIONS:
                        s = s.replace("</body>", "<script>addEventListener('load',()=>setTimeout(()=>{try{%s}catch(e){document.title='ERR '+e}},2500))</script></body>" % ACTIONS[STATE["demo"]])
                    if path == "/index.html": s = s.replace("<head>", "<head><script>localStorage.clear()</script>", 1)
                    data = s.encode()
                return self.send(data, TYPES.get(ext,"application/octet-stream"))
        sys.stderr.write("404 "+path+"\n"); self.send("", "text/plain", 404)
ThreadingHTTPServer(("127.0.0.1", PORT), H).serve_forever()
