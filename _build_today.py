#!/usr/bin/env python3
import json, re, os
from pathlib import Path
from datetime import date, timedelta

TODAY_ET = "2026-09-25"
DATE_HUMAN = "September 25, 2026"
DATE_TIME_HUMAN_HEADER = "Fri Sep 25, 2026, 7:30 AM ET"
WINDOW_SINCE = "Thu Sep 24, 2026, 7:30 AM ET"
WINDOW_HTML = (
    f"Window: stories published in the last 24 hours &mdash; since {WINDOW_SINCE}."
)
RUN_NARRATIVE = (
    "Friday 24-hour window (stories published since Thursday morning ET). 10 stories qualified from 24 "
    "outlets with in-window results, led by The Marshall Project on a Supreme Court-bound fight over ICE's "
    "indefinite mandatory detention; Sahan Journal on an $18.5M fraud settlement in Minnesota's Feeding Our "
    "Future scandal; New York Focus on the industry-and-Albany squeeze on NYC's climate law. Also: Louisville "
    "Public Media on a judge restoring journalists' White House access; The City Reporter on Mayor Mamdani's "
    "rent freeze surviving a court challenge for now; The Salt Lake Tribune and El Paso Matters both on "
    "data-center power fights, in Utah and on the Texas-New Mexico border; Block Club Chicago on CPS's "
    "11,500-student enrollment drop; Mission Local on San Francisco Democrats sticking with Flock surveillance "
    "cameras; NC Local on $75 million in Helene childcare relief still unpaid a year later."
)

PICKS = [
    {
        "rank": 1, "outlet": "The Marshall Project",
        "title": "ICE Says It Can Detain Immigrants As Long As It Wants. Will the Supreme Court Agree?",
        "url": "https://www.themarshallproject.org/2026/09/25/ice-mandatory-detention-immigration-judges",
        "time_chip": "Fri Sep 25 · 6:00 AM ET", "publishedAt": "2026-09-25T06:00:00-04:00",
        "why": "The case, headed toward the Supreme Court, will decide whether ICE can hold immigrants in mandatory detention indefinitely with no bond hearing before a judge — a ruling that would reshape detention conditions for tens of thousands of people nationwide.",
    },
    {
        "rank": 2, "outlet": "Sahan Journal",
        "title": "Partners in Nutrition will pay state $18.5M to settle food aid fraud claims",
        "url": "https://sahanjournal.com/news/partners-in-nutrition-federal-food-aid-fraud-settlement-minnesota/",
        "time_chip": "Thu Sep 24 · 10:00 AM ET", "publishedAt": "2026-09-24T10:00:00-04:00",
        "why": "Partners in Nutrition agreed to repay Minnesota $18.5 million after funneling more than $50 million meant for child nutrition into what investigators call a fraud scheme — the latest reckoning in the state's Feeding Our Future scandal, which has eroded trust in safety-net programs serving low-income immigrant families.",
    },
    {
        "rank": 3, "outlet": "New York Focus",
        "title": "Who's Behind the Push to Weaken NYC's Climate Law?",
        "url": "https://nysfocus.com/2026/09/24/coops-condos-united-rebny-local-law-97",
        "time_chip": "Thu Sep 24 · 6:00 AM ET", "publishedAt": "2026-09-24T06:00:00-04:00",
        "why": "The investigation traces a coordinated push by real estate groups and a homeowners' association to gut NYC's Local Law 97 climate mandate, running alongside Gov. Hochul's own effort to weaken the state's climate law — showing industry pressure closing in on climate rules from two directions at once.",
    },
    {
        "rank": 4, "outlet": "Louisville Public Media",
        "title": "Judge orders Trump administration to restore journalists' access to White House",
        "url": "https://www.lpm.org/news/2026-09-24/judge-orders-trump-administration-to-restore-journalists-access-to-white-house",
        "time_chip": "Thu Sep 24 · 2:00 PM ET", "publishedAt": "2026-09-24T14:00:00-04:00",
        "why": "A federal judge ordered the Trump administration to restore White House press access for journalists it had barred, a ruling that tests how much authority the executive branch has to control which reporters can cover it.",
    },
    {
        "rank": 5, "outlet": "The City Reporter (NYC)",
        "title": "Rent Freeze to Stay in Place For Now as Judge Holds Off on Decision",
        "url": "https://www.thecityreporter.nyc/2026/09/24/rent-freeze-lease-deadline-judge-lawsuit/",
        "time_chip": "Thu Sep 24 · 4:00 PM ET", "publishedAt": "2026-09-24T16:00:00-04:00",
        "why": "A judge declined to rule immediately on a lawsuit challenging Mayor Mamdani's rent freeze, leaving it in effect for now — keeping rent unchanged for hundreds of thousands of stabilized tenants while the legal fight continues.",
    },
    {
        "rank": 6, "outlet": "The Salt Lake Tribune",
        "title": "2 big data centers are coming to Utah's coal country. How they'll be powered has residents 'up in arms.'",
        "url": "https://www.sltrib.com/news/environment/2026/09/24/residents-up-arms-over-carbon/",
        "time_chip": "Thu Sep 24 · 9:00 AM ET", "publishedAt": "2026-09-24T09:00:00-04:00",
        "why": "Utah regulators are weighing how to power two new data centers proposed for the state's coal country, and nearby residents are fighting the plans — the latest flashpoint in a fast-growing conflict between AI infrastructure buildout and local power costs playing out from Utah to Texas.",
    },
    {
        "rank": 7, "outlet": "El Paso Matters",
        "title": "Oracle could defer Project Jupiter rent payments over power supply delays",
        "url": "https://elpasomatters.org/2026/09/24/project-jupiter-rent-force-majeure-new-mexico-oracle-ai-el-paso-data-center/",
        "time_chip": "Thu Sep 24 · 11:00 AM ET", "publishedAt": "2026-09-24T11:00:00-04:00",
        "why": "Oracle is asking to defer rent on its Project Jupiter AI data center near El Paso because it can't yet secure enough power — a delay that raises questions about who absorbs the cost when public subsidies are tied to projects that outpace the electric grid.",
    },
    {
        "rank": 8, "outlet": "Block Club Chicago",
        "title": "Chicago Public Schools Enrollment Drops By 11,500 Students",
        "url": "https://blockclubchicago.org/2026/09/24/chicago-public-schools-enrollment-drops-by-11500-students/",
        "time_chip": "Thu Sep 24 · 9:00 AM ET", "publishedAt": "2026-09-24T09:00:00-04:00",
        "why": "Chicago Public Schools lost 11,500 students this year, a drop steep enough to force new decisions on funding formulas, staffing and potential school closures in a district that already serves a majority-low-income population.",
    },
    {
        "rank": 9, "outlet": "Mission Local (SF)",
        "title": "S.F. Democratic Party stands behind Flock surveillance cameras in sweeping vote",
        "url": "https://missionlocal.org/2026/09/san-francisco-democratic-party-flock-cameras/",
        "time_chip": "Thu Sep 24 · 1:00 PM ET", "publishedAt": "2026-09-24T13:00:00-04:00",
        "why": "San Francisco's Democratic Party voted to keep backing Flock license-plate surveillance cameras despite privacy advocates' objections and evidence of industry lobbying — a reversal that puts a citywide surveillance tool back on track after it looked politically vulnerable.",
    },
    {
        "rank": 10, "outlet": "NC Local",
        "title": "NC received $75 million for childcare centers after Helene. Why haven't any providers received funds yet?",
        "url": "https://nclocal.org/2026/09/24/nc-received-75-million-for-childcare-centers-after-helene-why-have-no-providers-received-the-funds/",
        "time_chip": "Thu Sep 24 · 7:00 AM ET", "publishedAt": "2026-09-24T07:00:00-04:00",
        "why": "A year after Hurricane Helene, none of the $75 million North Carolina set aside for storm-damaged childcare centers has reached providers, leaving families in the hardest-hit western counties still without licensed care options.",
    },
]

COVERED_OUTLETS = set([
    "The Beacon (KC/MO)", "Block Club Chicago", "The City Reporter (NYC)", "The Colorado Sun",
    "CT Mirror", "Deep South Today", "El Paso Matters", "inewsource (San Diego)",
    "Louisville Public Media", "The Marshall Project", "Montana Free Press", "Mountain State Spotlight",
    "New York Focus", "Outlier Media (Detroit)", "Sahan Journal", "The Salt Lake Tribune",
    "Signal Ohio", "The Texas Tribune", "WFAE (Charlotte)", "Nashville Banner",
    "Cardinal News", "Fort Worth Report", "Mission Local (SF)", "NC Local",
])

WORKDIR = Path(os.environ["HOME"]) / "ajp-pub-today"
PUB_DIR = Path(os.environ["HOME"]) / "mnt" / "Downloads" / ".ajp-publish"
PUB_DIR.mkdir(parents=True, exist_ok=True)
(PUB_DIR / "archive").mkdir(parents=True, exist_ok=True)

with open(WORKDIR / "index.html", "r") as f:
    template = f.read()
with open(WORKDIR / "archive" / "index.json", "r") as f:
    archive_dates = json.load(f)
with open(WORKDIR / "archive" / "search-index.json", "r") as f:
    search_records = json.load(f)

if TODAY_ET not in archive_dates:
    archive_dates.append(TODAY_ET)
archive_dates = sorted(set(archive_dates), reverse=True)

search_records = [r for r in search_records if r.get("date") != TODAY_ET]
today_records = []
for p in PICKS:
    today_records.append({
        "date": TODAY_ET, "rank": p["rank"], "outlet": p["outlet"],
        "title": p["title"], "url": p["url"], "why": p["why"], "publishedAt": p["publishedAt"],
    })
search_records = today_records + search_records
search_records = sorted(search_records, key=lambda r: (r.get("publishedAt", ""), r.get("date", "")), reverse=True)

today_date = date.fromisoformat(TODAY_ET)
cutoff = (today_date - timedelta(days=365)).isoformat()
before_trim = len(search_records)
search_records = [r for r in search_records if r.get("date", "") >= cutoff]
trimmed = before_trim - len(search_records)
print(f"Search records: {before_trim} -> {len(search_records)} (trimmed {trimmed})")
TOTAL_RECORDS = len(search_records)
EARLIEST_DATE = min(r["date"] for r in search_records) if search_records else TODAY_ET

def attr_esc(s):
    return s.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;")
def html_text(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def fmt_earliest(d):
    y, m, dd = d.split("-")
    months = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    return f"{months[int(m)]} {int(dd)}, {y}"

story_blocks = []
for p in PICKS:
    top3 = " top3" if p["rank"] <= 3 else ""
    url_attr = attr_esc(p["url"]); title_attr = attr_esc(p["title"])
    title_text = html_text(p["title"]); why_text = html_text(p["why"])
    outlet_text = html_text(p["outlet"]); time_chip_text = html_text(p["time_chip"])
    block = f'''    <div class="story{top3}" data-url="{url_attr}">
      <div class="rank">{p["rank"]}</div>
      <div>
        <div class="outlet-row"><span class="outlet">{outlet_text}</span><span class="time-chip">{time_chip_text}</span>
          <button class="star-btn" type="button" data-url="{url_attr}" data-title="{title_attr}" aria-label="Save story" aria-pressed="false">&#9734;</button>
        </div>
        <div class="title"><a href="{url_attr}" target="_blank" rel="noopener">{title_text}</a></div>
        <div class="why"><span class="why-label">Why this matters:</span> {why_text}</div>
      </div>
    </div>'''
    story_blocks.append(block)
story_html = "\n".join(story_blocks)

out = template

out, n1 = re.subn(
    r'(<span class="refreshed">Updated</span>) [^<]*(</span>)',
    lambda m: m.group(1) + " " + DATE_TIME_HUMAN_HEADER + m.group(2),
    out, count=1)
print(f"#1 Header updated: {n1} subs")

out, n2 = re.subn(
    r'(<div class="window-line">)[\s\S]*?(</div>)',
    lambda m: m.group(1) + "\n      " + WINDOW_HTML + m.group(2),
    out, count=1)
print(f"#2 Window line: {n2} subs")

out, n3a = re.subn(r'(<span id="search-total">)\d+(</span>)', rf'\g<1>{TOTAL_RECORDS}\g<2>', out, count=1)
print(f"#3a search-total: {n3a} subs")
out, n3b = re.subn(
    r'(archived stories from )[A-Za-z]+ \d+, \d{4}( to )[A-Za-z]+ \d+, \d{4}( &mdash; )\d+( archived days\.)',
    lambda m: f'{m.group(1)}{fmt_earliest(EARLIEST_DATE)}{m.group(2)}{fmt_earliest(TODAY_ET)}{m.group(3)}{len(archive_dates)}{m.group(4)}',
    out, count=1)
print(f"#3b search-sub date range: {n3b} subs")

out, n4 = re.subn(
    r'(<section id="today-section">)[\s\S]*?(</section>\s*<section id="coverage-section">)',
    lambda m: m.group(1) + "\n" + story_html + "\n  " + m.group(2),
    out, count=1)
print(f"#4 Today section: {n4} subs")

out, n5 = re.subn(
    r'(<div style="margin-top:8px;"><strong>Today&rsquo;s run\.</strong>)[\s\S]*?(</div>\s*<div class="actions">)',
    lambda m: m.group(1) + " " + RUN_NARRATIVE + m.group(2),
    out, count=1)
print(f"#5 Footer narrative: {n5} subs")

new_archive_json = json.dumps(archive_dates, ensure_ascii=False)
out, n6 = re.subn(
    r'(<script type="application/json" id="archive-index">)[\s\S]*?(</script>)',
    lambda m: m.group(1) + new_archive_json + m.group(2),
    out, count=1)
print(f"#6 Archive index: {n6} subs")

new_search_json = json.dumps(search_records, ensure_ascii=False)
out, n7 = re.subn(
    r'(<script type="application/json" id="search-index">)[\s\S]*?(</script>)',
    lambda m: m.group(1) + new_search_json + m.group(2),
    out, count=1)
print(f"#7 Search index: {n7} subs")

m = re.search(r'const outlets = \[', out)
if not m: raise SystemExit("Could not find outlets array")
arr_start = m.end() - 1
depth = 0; i = arr_start; arr_end = None
while i < len(out):
    if out[i] == '[': depth += 1
    elif out[i] == ']':
        depth -= 1
        if depth == 0: arr_end = i + 1; break
    i += 1
if arr_end is None: raise SystemExit("Could not find outlets array end")
old_arr = json.loads(out[arr_start:arr_end])
for o in old_arr: o["covered"] = o["name"] in COVERED_OUTLETS
new_arr_text = json.dumps(old_arr, ensure_ascii=False)
out = out[:arr_start] + new_arr_text + out[arr_end:]
print(f"#8 Outlets updated: {sum(1 for o in old_arr if o['covered'])}/{len(old_arr)} covered")
missing = COVERED_OUTLETS - {o['name'] for o in old_arr}
if missing: print(f"WARNING: covered outlets not found in outlets array: {missing}")

out, n9 = re.subn(r'const TODAY_ET = "[\d\-]+";', f'const TODAY_ET = "{TODAY_ET}";', out, count=1)
print(f"#9 TODAY_ET: {n9} subs")

out, n10 = re.subn(r'const VIEWING_DATE = [^;]+;', 'const VIEWING_DATE = null;', out, count=1)
print(f"#10 VIEWING_DATE (dashboard, null): {n10} subs")

dashboard_path = PUB_DIR / "index.html"
with open(dashboard_path, "w") as f: f.write(out)
print(f"Wrote {dashboard_path} ({len(out)} chars)")
(WORKDIR / "index.html").write_text(out)
print(f"Wrote {WORKDIR / 'index.html'} (repo copy)")

snap = out
snap, ns1 = re.subn(
    r'<span class="meta-pill">Top picks, 49 outlets</span><span><span class="dot"></span> <span class="refreshed">Updated</span>[^<]*</span>',
    f'<span class="meta-pill snapshot">Archive snapshot</span><span class="snapshot-stamp">Snapshot from {DATE_HUMAN}</span>',
    snap, count=1)
print(f"snapshot header swap: {ns1}")
snap, ns2 = re.subn(r'const VIEWING_DATE = (?:null|"[\d\-]+");', f'const VIEWING_DATE = "{TODAY_ET}";', snap, count=1)
print(f"snapshot VIEWING_DATE: {ns2}")

archive_html_path = PUB_DIR / "archive" / f"{TODAY_ET}.html"
with open(archive_html_path, "w") as f: f.write(snap)
print(f"Wrote {archive_html_path} ({len(snap)} chars)")
(WORKDIR / "archive" / f"{TODAY_ET}.html").write_text(snap)
print(f"Wrote {WORKDIR}/archive/{TODAY_ET}.html (repo copy)")

with open(PUB_DIR / "archive" / "index.json", "w") as f: json.dump(archive_dates, f, ensure_ascii=False)
(WORKDIR / "archive" / "index.json").write_text(json.dumps(archive_dates, ensure_ascii=False))
print(f"Wrote archive/index.json: {len(archive_dates)} dates")

with open(PUB_DIR / "archive" / "search-index.json", "w") as f: json.dump(search_records, f, ensure_ascii=False)
(WORKDIR / "archive" / "search-index.json").write_text(json.dumps(search_records, ensure_ascii=False))
print(f"Wrote archive/search-index.json: {len(search_records)} records")
print("Build complete.")
