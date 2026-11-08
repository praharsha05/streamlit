import csv
import os
from datetime import datetime
from html import escape as e

import streamlit as st

st.set_page_config(page_title="Analyst Shubhi | Data Analyst & Career Mentor", page_icon="📊",
                   layout="wide", initial_sidebar_state="collapsed")


def html(s: str):
    """Strip indentation and blank lines so markdown never treats HTML as a code block."""
    st.markdown("\n".join(l.strip() for l in s.splitlines() if l.strip()), unsafe_allow_html=True)


# =================================================================== CONTENT
NAME = "Analyst Shubhi"
TAGLINE = "Data Analyst | Career Mentor | Hyderabad"
BIO = ("Hi, I’m Shubhanshi! I’m on a mission to help you land your dream job in the Analytics field. "
       "Let’s cut through the noise and get you hired. Let’s grow together.")
PHOTO = "https://static.topmate.io/profile_pic_1890632_57216a9f-a7a2-4f14-a7bb-ca187774bb26.jpeg"  # download & host your own
INSTAGRAM = "https://www.instagram.com/analyst_shubhi"
STATS = [("4.9/5", "177 ratings"), ("7.1k+", "bookings"), ("135", "testimonials")]
CLIENTS = ["Apple", "ServiceNow", "AT&T", "Infosys"]

TM = "https://topmate.io/analyst_shubhi/"
# Razorpay payment links: when you create one, paste it here keyed by the Topmate id.
# Anything not listed here keeps pointing at Topmate.
RAZORPAY = {
    "2350025": "https://pages.razorpay.com/pl_TxaeUt4h07qPGm/view",  # PL SQL PROJECT GUIDE
}
# Optional: override/add links from Streamlit Secrets without editing code, e.g. in Secrets:
#   [razorpay_links]
#   "2047126" = "https://pages.razorpay.com/pl_XXXX/view"
try:
    RAZORPAY.update(dict(st.secrets["razorpay_links"]))
except Exception:
    pass  # no secrets configured -> use the dictionary above

# (id, type, title, description, price, badge, meta)
SERVICES = [
    ("2350025", "Digital Product", "PL SQL PROJECT GUIDE", "PL SQL PROJECT", 49, "", ""),
    ("2047126", "Digital Product", "Full Python Notes", "Full Python Notes for Data analysis.", 99, "", ""),
    ("2263649", "Digital Product", "AI Crash Course for Beginners", "Learn GenAI, LLMs, RAG & AI Agents", 99, "", ""),
    ("2265773", "Digital Product", "Snowflake Complete Notes 🖇️", "Snowflake ❄️ Complete Notes 📝", 151, "Best Seller", ""),
    ("1947599/pay", "Priority DM", "Ask me anything", "Priority DM with a reply within a day.", 199, "", "1 day reply"),
    ("1951828", "1:1 Call", "Career guidance and Mentorship", "End-to-End Data Analyst Mentorship", 699, "Popular", "Video call · 30 mins"),
    ("1952372", "Digital Product", "Data analyst ROADMAP for freshers", "A step-by-step roadmap to get started.", 20, "Popular", ""),
    ("1953035", "1:1 Call", "Career Guidance + Queries (30-Min Strategy Call)", "A focused 1:1 session to clear your career confusion.", 899, "", "Video call · 60 mins"),
    ("1947597", "1:1 Call", "Resume & Portfolio Building", "Build a resume and portfolio that gets shortlisted.", 999, "", "Video call · 60 mins"),
    ("1953056", "1:1 Call", "Mock Interview", "Mock Interview For Data Analysis", 699, "", "Video call · 30 mins"),
    ("2022373", "Digital Product", "POWER BI GUIDE", "Power BI Guide for beginners", 49, "", ""),
    ("2061769", "Digital Product", "Data Analysis Crash Course (Beginner to Job-Ready)", "Data Analysis Crash Course: Beginner to Job-Ready", 99, "", ""),
    ("2120294", "Digital Product", "DATA ENGINEERING NOTES", "All-in-one Data Engineering Notes to help you learn faster.", 151, "", ""),
    ("2223853", "Digital Product", "Premium Resource 📊📈", "All-in-one Resources to help you learn faster ✅", 399, "", ""),
    ("1949422", "Digital Product", "All Data Analytics Resource Bundle", "All-in-one Data Analyst resources to help you learn faster.", 99, "", ""),
    ("1934277/pay", "Priority DM", "Direct Chat for Data Analytics Mentorship", "Get direct 1:1 guidance on Data Analytics.", 99, "", "2 days reply"),
    ("1967027", "1:1 Call", "Fresher to Data Analyst – Career Strategy Call", "Career strategy for freshers moving into analytics.", 899, "", "Video call · 60 mins"),
    ("1954920", "Digital Product", "Excel shortcuts", "Excel shortcuts cheat sheet.", 20, "", ""),
    ("1967014", "1:1 Call", "Data Analyst Resume Review + Improvement", "Detailed review and improvement of your resume.", 899, "", "Video call · 60 mins"),
]
FILTERS = ["All Services", "1:1 Call", "Priority DM", "Digital Product"]

ABOUT = """Hi, I’m Shubhanshi, a Data Analyst with 5+ years of industry experience working with global clients like Apple, ServiceNow, AT&T and Infosys. I specialize in data analysis, dashboards, reporting, and business insights using tools like SQL, Power BI, Excel, and Snowflake. Over the years, I’ve worked on real client projects, partner analytics, and business reporting solutions that helped teams make better data-driven decisions."""
ABOUT_FOR = ["A beginner who wants to start a career in Data Analytics",
             "Someone preparing for data analyst interviews",
             "A working professional who wants to upskill",
             "Someone who needs guidance on tools, projects, and career direction"]
ABOUT_HELP = ["How to start in Data Analytics from scratch", "Resume & portfolio building",
              "Interview preparation (SQL, Power BI, case questions)",
              "Real industry project understanding", "Career transition into data roles"]

TESTIMONIALS = [
    ("This session with Shubhanshi provided a clear understanding of what interviewers actually expect from the candidates - strong fundamentals, structured problem solving, and the ability to think in terms of business impact rather than just tools or syntax. Overall, the guidance was practical and honest. Looking forward to have more sessions with her.", "Kamaldeep Ch"),
    ("I found the session very useful. Shubhanshi provided clear direction on how to position my background. what roles to target and how to plan my next steps. The guidance was practical and easy to follow. It helped me gain clarity and confidence moving forward.", "Sree Ravali"),
    ("I had a really insightful session with Shubhanshi, honestly felt like talking to a big sister. She gave me a clear roadmap and helped me understand exactly where I should focus. Her suggestions were practical, supportive, and easy to follow. Overall, it was a very comforting and motivating experience..!!!", "Priya Peddamallu"),
    ("I recently had a video consultation with Subhanshi Mishra regarding my journey into Data Analytics, and it was an extremely valuable experience. She provided clear, structured, and practical guidance on how to proceed in this field. What stood out the most was her ability to simplify complex concepts and give actionable advice tailored to my situation. Her approach was professional, supportive, and highly insightful, which gave me much-needed clarity and confidence.", "Ujjwal"),
    ("You made the session very interactive and gave the right path to start according to the market requirements. Thanks for the proper guidance.", "Shreyanshu Das"),
    ("I have a wonderful experience in one on one live google meet meeting with mam she talks about everything of the course and roadmap of data analyst and also she is a very knowledge person her teaching and doubt solving techniques are so good and helpful thaks god for meet this person who supports and share her knowledge to everyone's who want s to become a data analyst in his life.", "Vishnu"),
    ("I love the way you help me MAM and your guidance and support have played an important role in helping me move closer to my dream of becoming a data analyst. Through your explanations and learning resources, I have improved my understanding of data analysis concepts, tools, and practical skills. Your help has motivated me to stay focused, practice consistently, and overcome challenges during my learning journey. Because of this support, I feel more confident in my abilities and more determined to achieve my goal of building a successful career as a data analyst.", "Usman Akmal"),
    ("I was struggling to get interview calls despite applying for multiple companies She provided me a structured breakdown of my resume and helped me correct my targeting strategy The session was honest and practical not generic advice Highly valuable for anyone serious about getting in analytics roles", "Nikhilesh varasala"),
]

FAQS = [
    ("How to become a data analyst in India?", "If you are wondering how to become a data analyst, the proven path for Indian freshers is: strengthen Excel first, then learn SQL deeply (the most-tested skill in interviews), then Power BI for dashboards, followed by basic Python and statistics. Build two or three end-to-end projects on real datasets, turn them into a one-page resume and portfolio, and start applying while preparing for interviews. With consistent effort of 4–6 months, freshers from any stream can become job-ready without an expensive degree."),
    ("What should a data analyst roadmap for freshers include?", "A practical data analyst roadmap for freshers should move in this order: Excel (formulas, pivot tables, charts) → SQL (joins, aggregations, window functions) → Power BI (dashboard building, DAX basics) → statistics fundamentals → Python with pandas as an add-on. The final stage must be 2–3 portfolio projects plus resume and interview preparation. Avoid the common mistake of learning five tools at once — depth in SQL and one visualisation tool beats surface-level knowledge of many."),
    ("Is the data analyst roadmap 2026 different from earlier years?", "The core of the data analyst roadmap 2026 is still Excel, SQL, Power BI and Python, but hiring expectations have risen. Employers increasingly want familiarity with cloud data platforms such as Snowflake, comfort using AI tools to work faster, and the ability to explain insights to non-technical business teams. Freshers who combine the classic skill set with one cloud warehouse and strong data storytelling stand out noticeably in 2026 applications."),
    ("Is a data analyst roadmap PDF enough to become job-ready?", "A data analyst roadmap PDF works well as a checklist, but a PDF alone will not get you hired. The roadmap only tells you what to learn; job-readiness comes from executing it — writing SQL queries daily, building dashboards on real datasets, and getting feedback on your projects from mentors or peers. Pair the PDF with consistent hands-on practice so you spend your months building skills instead of just collecting resources."),
    ("Can I follow the data analyst roadmap after 10th?", "Yes — starting the data analyst roadmap after 10th gives you a multi-year head start. Begin with school-level maths and statistics, then Excel, and gradually basic SQL and Python. Since most analyst jobs in India require a bachelor's degree, use your 11th, 12th and college years to build projects and certifications. You will then graduate with a portfolio most freshers simply do not have."),
    ("How to crack a data analyst interview without work experience?", "If you want to know how to crack a data analyst interview without experience, replace experience with proof: be able to write SQL queries live, walk through one project end-to-end (problem → data → cleaning → analysis → business insight), and practise guesstimates and case questions out loud. Interviewers do not expect freshers to have corporate exposure — they evaluate fundamentals, structured thinking, and honesty about what you have not used yet."),
    ("How long does data analyst interview preparation take?", "Focused data analyst interview preparation usually takes 6–8 weeks. Spend 3–4 weeks on daily SQL practice (this is where most candidates get eliminated), 1–2 weeks revising Excel, Power BI and statistics, one week turning your projects into impact stories, and the final week on mock interviews and company research. Skipping mock interviews is the most common reason well-prepared candidates still get rejected."),
    ("What are the most common data analyst interview questions?", "Common data analyst interview questions fall into five buckets: SQL (joins, GROUP BY, window functions, handling nulls and duplicates), Excel (VLOOKUP/XLOOKUP, pivot tables, data cleaning), Power BI (measures vs calculated columns, DAX basics, dashboard design), statistics (averages, distributions, correlation, A/B testing), and project deep-dives where you explain your work and its impact. Many companies in India also add a guesstimate or case-study round to test business thinking."),
    ("What are common data analyst interview questions and answers for freshers?", "Most data analyst interview questions and answers for freshers stay close to fundamentals — types of SQL joins, WHERE vs HAVING, primary key vs foreign key, cleaning a messy dataset, and a walkthrough of your best project. What interviewers actually judge is how you structure answers: state your approach first, add the details, finish with the result. Memorised answers fall apart under follow-up questions, so practise explaining concepts in your own words."),
    ("What are common data analyst interview questions for 3 years of experience?", "Data analyst interview questions for 3 years of experience shift from definitions to ownership. Expect advanced SQL (window functions, query optimisation), why you designed a dashboard the way you did, the measurable business impact of your analysis, how you handled conflicting stakeholder requirements, and why you want to switch. Prepare two or three detailed project stories with numbers — at this level, impact decides offers more than tool knowledge."),
    ("Is it enough to prepare from a data analyst interview questions and answers PDF?", "A data analyst interview questions and answers PDF is useful for revision and for spotting question patterns, but it is not enough on its own. Interviews test live performance: writing SQL without references, thinking aloud through a case, and communicating clearly under pressure. Use the PDF to shortlist topics, then practise on an actual SQL editor, answer questions out loud, and complete at least a few mock interviews before the real one."),
    ("How to make a data analyst resume that gets shortlisted?", "If you are unsure how to make a data analyst resume that gets shortlisted, follow this structure: a skills section at the top (SQL, Excel, Power BI, Python), two or three projects written as “action + tool + measurable result” bullets, then education and certifications. Mirror keywords from each job description so your resume clears ATS filters, keep it to one page as a fresher, and quantify everything — “cut reporting time by 30%” beats “responsible for reporting”."),
    ("How to make a data analyst resume with no experience?", "Wondering how to make a data analyst resume with no experience? Treat projects as your experience — academic projects, self-built dashboards on public datasets, internships, and certifications all count. A strong data analyst resume for freshers opens with skills, leads with quantified project outcomes, and ends with education and certifications. Publish your dashboards (Power BI service, GitHub, Tableau Public) and add links so recruiters can actually verify your work."),
    ("Should I use a data analyst resume template?", "Yes — a data analyst resume template saves formatting time, but choose the right kind. Pick a simple, single-column, ATS-friendly layout with standard section headings; avoid graphic-heavy templates with photos, icons, tables or multiple columns, because ATS software often misreads them and rejects the file before a human ever sees it. Use the template only for structure — your keywords, projects and numbers must be customised for every application."),
    ("What should a data analyst resume for 3 years of experience highlight?", "A data analyst resume for 3 years of experience should highlight business impact over tool lists — for example, “automated weekly reporting in SQL, saving 10 hours a week” or “built Power BI dashboards used by 200+ users”. Show end-to-end ownership of projects, advanced skills such as window functions, Snowflake or Python automation, and stakeholder management. Remove college projects and coursework, cap the resume at two pages, and lead every bullet with a number wherever possible."),
]

# ====================================================================== CSS
html("""
<style>
:root{--bg:#fffdf8;--alt:#f6f1e7;--card:#fff;--ink:#16161a;--mut:#5d5d66;--line:#e6e0d3;--acc:#ff5b3a;--btn:#16161a;--btnt:#fff;--ph1:#ffd9a8;--ph2:#ff9b7a}
@media(prefers-color-scheme:dark){:root{--bg:#121214;--alt:#1a1a1e;--card:#1f1f24;--ink:#f4f1ea;--mut:#a5a5ae;--line:#2e2e35;--btn:#f4f1ea;--btnt:#121214;--ph1:#5a3a22;--ph2:#7a2f1f}}
header[data-testid="stHeader"],footer,#MainMenu{display:none!important}
.stApp{background:var(--bg);color:var(--ink);font-family:Inter,system-ui,-apple-system,"Segoe UI",sans-serif}
.block-container{max-width:100%!important;padding:0!important}
[data-testid="stVerticalBlock"]{gap:0!important}
.stApp a{text-decoration:none;color:inherit}
.w{max-width:1180px;margin:0 auto;padding:0 24px}
.stApp h1,.stApp h2,.stApp h3{line-height:1.15;margin:0;padding:0;letter-spacing:-.02em;color:var(--ink)}
.stApp h1{font-size:clamp(38px,6vw,64px)}.stApp h2{font-size:clamp(30px,4vw,42px)}.stApp h3{font-size:19px}
.stApp p{margin:0 0 14px;font-size:17px;line-height:1.6}
.sec{padding:80px 0}.alt{background:var(--alt)}
.hd{display:flex;align-items:center;justify-content:space-between;padding:20px 0;gap:16px;flex-wrap:wrap}
.logo{font-weight:800;font-size:20px}
.nav{display:flex;gap:28px;font-weight:500}.nav a:hover{color:var(--acc)}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;padding:13px 24px;border-radius:999px;background:var(--btn);color:var(--btnt)!important;font-weight:600;border:2px solid var(--btn)}
.btn.o{background:transparent;color:var(--ink)!important;border-color:var(--ink)}
.btn.sm{padding:9px 18px;font-size:15px}
.tag{display:inline-flex;align-items:center;gap:8px;font-weight:600;font-size:15px;margin-bottom:18px}
.tag:before{content:"";width:10px;height:10px;border-radius:50%;background:var(--acc)}
.hero{display:grid;grid-template-columns:1.1fr .9fr;gap:48px;align-items:center;padding:56px 0 64px}
.hero p.l{font-size:19px;color:var(--mut);max-width:560px;margin:22px 0 28px}
.row{display:flex;gap:14px;flex-wrap:wrap}
.ph{border-radius:24px;background:linear-gradient(135deg,var(--ph1),var(--ph2));overflow:hidden}
.ph img{width:100%;height:100%;object-fit:cover;display:block}
.portrait{aspect-ratio:4/5;max-width:440px;margin-left:auto}
.stats{display:flex;gap:36px;flex-wrap:wrap;margin-bottom:26px}
.stats b{display:block;font-size:28px;line-height:1.1}.stats span{color:var(--mut);font-size:14px}
.feat{padding:30px 0;border-top:1px solid var(--line);border-bottom:1px solid var(--line);text-align:center}
.feat p{color:var(--mut);font-weight:500}
.logos{display:flex;justify-content:space-around;gap:24px;flex-wrap:wrap}
.logos b{font-size:24px;color:var(--mut);opacity:.75}
.head{text-align:center;max-width:680px;margin:0 auto 36px}.head p{color:var(--mut)}
.g3{display:grid;grid-template-columns:repeat(3,1fr);gap:24px}
.card{background:var(--card);border:1px solid var(--line);border-radius:22px;padding:26px;display:flex;flex-direction:column}
.card p{color:var(--mut);font-size:15.5px;margin-top:8px;flex:1}
.svc .top{display:flex;justify-content:space-between;align-items:center;gap:8px;margin-bottom:14px;font-size:13.5px;color:var(--mut);font-weight:600}
.badge{background:var(--acc);color:#fff;border-radius:999px;padding:3px 11px;font-size:12.5px;font-weight:700}
.price{font-size:26px;font-weight:800;margin:6px 0 14px}
.price small{font-size:13px;font-weight:500;color:var(--mut)}
.more{font-weight:600;color:var(--acc)!important}
.two{display:grid;grid-template-columns:1fr 1fr;gap:56px;align-items:start}
.two p,.two li{color:var(--mut)}
.two li{margin-bottom:6px;font-size:16.5px}
.two h3{margin:22px 0 10px}
.cols{column-count:3;column-gap:24px}
.cols .card{break-inside:avoid;margin-bottom:24px}
.cols p{color:var(--ink);font-size:15.5px}
.stars{color:#f5a623;letter-spacing:3px;margin-bottom:10px}
.who{margin-top:14px;font-weight:700}
details{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:18px 22px;margin-bottom:12px;max-width:860px;margin-left:auto;margin-right:auto}
summary{font-weight:700;cursor:pointer;font-size:17px}
details p{color:var(--mut);margin:12px 0 0;font-size:16px}
.nl{text-align:center;max-width:700px;margin:0 auto}.nl p{color:var(--mut)}
.ft{background:var(--ink);color:var(--bg);padding:48px 0 24px}
.ft .fb{display:flex;justify-content:space-between;flex-wrap:wrap;gap:12px;font-size:14px}
.ft a{margin-left:18px;opacity:.8}.ft span{opacity:.8}
.st-key-filterbar{background:var(--alt);padding:8px 24px 32px;width:100%}
.st-key-filterbar [data-testid="stHorizontalBlock"]{max-width:880px;margin:0 auto!important;gap:16px!important}
.st-key-filterbar button{width:100%;min-height:0;padding:12px 18px;border-radius:999px;border:1.5px solid var(--line);background:var(--card);color:var(--ink);transition:border-color .15s}
.st-key-filterbar button:hover{border-color:var(--ink);color:var(--ink)}
.st-key-filterbar button p{margin:0;font-family:Inter,system-ui,-apple-system,"Segoe UI",sans-serif;font-size:15.5px;font-weight:600;letter-spacing:-.01em;color:inherit}
.st-key-filterbar button[data-testid="stBaseButton-primary"],.st-key-filterbar button[kind="primary"]{background:var(--btn);border-color:var(--btn);color:var(--btnt)}
.st-key-filterbar button[data-testid="stBaseButton-primary"]:hover,.st-key-filterbar button[kind="primary"]:hover{color:var(--btnt)}
.st-key-filterbar button:focus-visible{outline:3px solid var(--acc);outline-offset:2px}
[data-testid="stForm"]{max-width:520px;margin:24px auto 0;border:2px dashed var(--line);border-radius:18px;padding:24px;background:transparent}
[data-testid="stForm"] button{border-radius:999px;background:var(--btn);color:var(--btnt);border:0;font-weight:600}
@media(max-width:900px){.hero,.two{grid-template-columns:1fr;gap:32px}.g3{grid-template-columns:1fr 1fr}.cols{column-count:2}.nav{display:none}.sec{padding:56px 0}.portrait{margin:0 auto}}
@media(max-width:600px){.g3{grid-template-columns:1fr}.cols{column-count:1}}
</style>
""")

# ================================================================ HEADER+HERO
stats = "".join(f"<div><b>{a}</b><span>{b}</span></div>" for a, b in STATS)
clients = "".join(f"<b>{c}</b>" for c in CLIENTS)
html(f"""
<div class="w">
<div class="hd"><a class="logo" href="#">{e(NAME)}</a>
<div class="nav"><a href="#services">Services</a><a href="#about">About</a><a href="#reviews">Testimonials</a><a href="#faq">FAQ</a></div>
<a class="btn sm" href="#services">Book now</a></div>
<div class="hero">
<div><div class="tag">{e(TAGLINE)}</div>
<h1>Let’s cut through the noise and get you hired.</h1>
<p class="l">{e(BIO)}</p>
<div class="stats">{stats}</div>
<div class="row"><a class="btn" href="#services">Explore services</a><a class="btn o" href="{INSTAGRAM}" target="_blank">Follow on Instagram</a></div></div>
<div class="ph portrait"><img src="{PHOTO}" alt="Shubhanshi" onerror="this.style.display='none'"></div>
</div>
<div class="feat"><p>5+ years of experience with global clients</p><div class="logos">{clients}</div></div>
</div>
""")

# ====================================================================== ABOUT
li = lambda items: "".join(f"<li>{e(i)}</li>" for i in items)
html(f"""
<div class="sec" id="about"><div class="w two">
<div><div class="tag">About me</div><h2>Real client experience, in plain language</h2></div>
<div><p>{e(ABOUT)}</p>
<h3>I’m here to help you if you are:</h3><ul>{li(ABOUT_FOR)}</ul>
<h3>I can guide you on:</h3><ul>{li(ABOUT_HELP)}</ul></div>
</div></div>
""")

# ================================================================== SERVICES
html("""
<div class="alt" id="services" style="padding:80px 0 12px"><div class="w">
<div class="head"><h2>Services</h2><p>Digital products start from ₹20. Pick a category or browse everything.</p></div>
</div></div>
""")
if "cat" not in st.session_state:
    st.session_state.cat = FILTERS[0]
with st.container(key="filterbar"):
    for col, name in zip(st.columns(len(FILTERS), gap="medium"), FILTERS):
        if col.button(name, key=f"f_{name}", use_container_width=True,
                      type="primary" if st.session_state.cat == name else "secondary"):
            st.session_state.cat = name
            st.rerun()
choice = st.session_state.cat


def card(sid, typ, title, desc, price, badge, meta):
    link = RAZORPAY.get(sid, TM + sid)
    label = {"Digital Product": "Get it now", "1:1 Call": "Book a call", "Priority DM": "Send a message"}[typ]
    b = f'<span class="badge">{badge}</span>' if badge else ""
    m = f"{typ} · {meta}" if meta else typ
    return (f'<div class="card svc"><div class="top"><span>{e(m)}</span>{b}</div>'
            f'<h3>{e(title)}</h3><p>{e(desc)}</p><div class="price">₹{price}</div>'
            f'<a class="btn" href="{link}" target="_blank" rel="noopener">{label}</a></div>')


cards = "".join(card(*s) for s in SERVICES if choice == "All Services" or s[1] == choice)
html(f'<div class="alt" style="padding:12px 0 84px"><div class="w"><div class="g3">{cards}</div></div></div>')

# =============================================================== TESTIMONIALS
t = "".join(f'<div class="card"><div class="stars">★★★★★</div><p>“{e(q)}”</p><div class="who">{e(n)}</div></div>'
            for q, n in TESTIMONIALS)
html(f"""
<div class="sec" id="reviews"><div class="w">
<div class="head"><h2>Testimonials</h2><p>135 people have shared feedback after working with me. Here are a few.</p></div>
<div class="cols">{t}</div></div></div>
""")

# ========================================================================= FAQ
f = "".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in FAQS)
html(f"""
<div class="sec alt" id="faq"><div class="w">
<div class="head"><h2>Frequently asked questions</h2></div>{f}</div></div>
""")

# ================================================================= NEWSLETTER
html("""
<div class="sec" style="padding-bottom:0"><div class="w nl">
<h2>Get free data analytics tips</h2><br><br>
<p>Join my mailing list for roadmaps, interview questions, and new resources as I publish them.</p></div></div>
""")
with st.form("newsletter", clear_on_submit=True):
    email = st.text_input("Email address", placeholder="you@example.com")
    if st.form_submit_button("Subscribe", use_container_width=True):
        if "@" in email and "." in email:
            new = not os.path.exists("subscribers.csv")
            with open("subscribers.csv", "a", newline="") as fh:
                w = csv.writer(fh)
                if new:
                    w.writerow(["email", "subscribed_at"])
                w.writerow([email.strip(), datetime.now().isoformat(timespec="seconds")])
            st.success("You’re in! Watch your inbox.")
        else:
            st.error("Enter a valid email address.")

# ===================================================================== FOOTER
html(f"""
<div class="ft" style="margin-top:80px"><div class="w"><div class="fb">
<span>© {datetime.now().year} {e(NAME)}. All rights reserved.</span>
<span><a href="{INSTAGRAM}" target="_blank">Instagram</a><a href="#">Privacy Policy</a><a href="#">Terms</a><a href="#">Refund Policy</a></span>
</div></div></div>
""")
