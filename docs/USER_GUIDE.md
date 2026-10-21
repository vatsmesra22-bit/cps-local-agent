# CSP GPS Complaints – poora system kaise chalta hai (aasan guide)

## Ye system kya karta hai
DCs CSP pe jaake **SBI CSP Visit app** se visit mark karte hain. GPS, location, radius ya app ki dikkat
se visit nahi hota, to wo **"Kiosk Team Eko"** WhatsApp group mein photo aur CSP ID daal dete hain.

Ye system un messages ko padhta hai aur:
- sirf **"app se visit nahi ho paya"** wali complaints chhaanta hai (check-in, notice, "visit done" wagairah chhod deta hai)
- har complaint ka **CSP ID, date, kisne bheja, problem, distance, status** nikalta hai
- batata hai **ab kya karna hai** aur kaunsi complaint **follow up / escalate** karni hai
- sab kuch **ek Excel file** aur **ek dashboard** mein rakhta hai, 22 Sep 2026 se aaj tak

---

## Ek baar ka setup (naye / office PC pe) – 15 minute

**Step 1 – Folder copy karo**
Ye poora folder us PC pe **chhote path** pe copy karo, jaise `C:\CSP-GPS`.
`data` folder bhi saath copy karna; isme purane record ID aur aapke manual edits hain.

**Step 2 – Python install karo (agar nahi hai)**
https://www.python.org/downloads/ → Python 3.11 ya naya → install karte time
**"Add python.exe to PATH"** pe tick lagao.

**Step 3 – Setup.bat double-click karo**
Ye packages install karega, `.env` file banayega, test chalayega aur Desktop pe
**"CSP GPS - Update Report"** shortcut bana dega.

**Step 4 – Roz apne aap chalne ke liye (agent)**
1. Us PC pe **Claude app** install karke sign in karo.
2. Chrome mein **Claude extension** lagao: https://chromewebstore.google.com/detail/fcoeoabgfenejglbffodgkkbkcdhcgfn → sign in.
3. Usi Chrome mein **web.whatsapp.com** kholo aur us number se QR scan karo jo "Kiosk Team Eko" group mein hai.
   Office ka shared number best hai, kisi ek insaan ka personal number nahi.
4. **Taala lagao:** project folder ki `.env` file Notepad mein kholo aur ye do lines bharo:
   ```
   WHATSAPP_ALLOWED_PROFILE_NAME=WhatsApp mein jo naam dikhta hai
   WHATSAPP_ALLOWED_PHONE_LAST4=1234
   ```
   Agent sirf usi account ko padhega. PC pe koi aur WhatsApp khula ho to wo kuch nahi kholega.
   Ye khaali ho to agent WhatsApp padhta hi nahi.
5. Claude app → **Scheduled** → **New task** → `agent/DAILY_AGENT_TASK.md` ka text paste karo,
   `<PROJECT_FOLDER>` ki jagah is folder ka path likho, aur time **10:00 AM aur 3:00 PM** rakho.

---

## Roz kya hota hai (khud se)

| Time | Kya hota hai |
|---|---|
| **10:00 AM, 3:00 PM** | Agent WhatsApp Web pe group ke naye messages **sirf padhta hai** (kuch bhejta nahi) |
| | Downloads mein naya WhatsApp export ho to wo bhi utha leta hai |
| | Excel aur dashboard update karta hai |
| | Claude app mein chhota summary deta hai: aaj kitni nayi, kitni pending, kise escalate karna hai |

**Dekhna kahan hai:**
- **Dashboard:** http://csp-gps.localhost:8501 (sabse upar "Aaj ki nayi complaints" aur "What to do now")
- **Excel (SBI ko yahi bhejni hai):** `output\CSP_GPS_Issue_Report.xlsx`

---

## 🤖 Agent kya khud karta hai
- Har run (10:00, 15:00) ke baad dashboard ke **🤖 Agent** tab mein dikhata hai: nayi complaints, kya band hua,
  kya escalate karna hai.
- Jis complaint wale CSP ka baad mein **app se visit ho gaya**, use khud **band (Resolved)** kar deta hai,
  saboot ke saath.
- **WhatsApp messages taiyaar karta hai:** Ma'am ko roz ka update, Amit ji (tech support) ko GPS/app wale CSPs,
  Ganesh ji ko mapping/lat-long wale CSPs, aur DCs ko "CSP ID bhejo". Message ke kone mein copy button hai,
  copy karke WhatsApp mein bhejo. **Agent khud kabhi kuch nahi bhejta.**
- Naam badalne hain to `config/settings.yaml` mein `agent_contacts`.

## Aapko kya karna hai

1. **Dashboard ka "What to do now" dekho.** Har complaint ke saath likha hai kya karna hai.
2. **Excel ke "Detailed Issue Tracker" sheet mein** *Resolution Status*, *Assigned To*, *Resolution Notes* update karo.
   Agle update mein bhi ye bache rahenge.
3. **"To verify" / "double-check" wali complaints** WhatsApp mein ek baar khol ke confirm kar lo.

---

## App ki visit report (SBI CSP Visit App)
App se "Visit report ... .xlsx" download karke **Downloads** mein daal do. Agle update pe ye apne aap aa jayegi.
Dashboard ke **🗓 App Visits** tab mein dikhega:
- kitne visits hue, kis circle mein aur kis DC ne kiye
- complaint wale kaun se CSP ka baad mein app se visit hua ✅ aur kiska nahi ❌

DC ke naam dikhane ke liye `config/dc_users.csv` banao: `username,dc_name` (jaise `BC1A855398,Anil Sharma`).

## Agar WhatsApp Web connected nahi hai (backup – 2 minute)
Phone pe group kholo → **⋮ → More → Export chat → Include media** → Gmail pe khud ko bhejo →
laptop pe download karo (Downloads folder) → Desktop pe **"CSP GPS - Update Report"** double-click.
Ek group ke kai exports daal do, koi message do baar nahi ginega.

---

## Kuch gadbad ho to

| Dikkat | Kya karo |
|---|---|
| Dashboard nahi khul raha | "CSP GPS - Update Report" double-click karo |
| Summary mein "WhatsApp Web not read" | Chrome mein Claude extension pe dobara sign in karo; WhatsApp Web logged in hai, check karo |
| 10/3 baje kuch nahi hua | Claude app khula tha? Laptop sleep mein to nahi tha? App khulte hi task chal jata hai |
| Koi complaint chhoot gayi ya galat aayi | Message ka text note karke rule theek karwao (`src/csp_gps/extract.py`, dekho `docs/ARCHITECTURE.md`) |
| "Kya karna hai" ka text badalna hai | `config/settings.yaml` mein `suggested_actions` |
| Kuch aur | `logs\process.log` aur `logs\daily.log` dekho |

---

## Zaroori baatein
- Phone numbers report mein chhupe rehte hain (`98XXX XX210`).
- Saara data isi computer pe rehta hai, kahin upload nahi hota.
- Agent WhatsApp pe **sirf padhta hai**, kabhi kuch bhejta, delete ya badalta nahi.
- Jo jaankari message mein nahi likhi (jaise district), wo **"Not Available"** dikhti hai. System apne se kuch nahi bharta.
