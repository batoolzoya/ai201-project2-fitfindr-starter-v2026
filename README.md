# FitFindr

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every
> command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> python app.py listings --full -n 6      # read the data (Milestone 1)
> python app.py fields                    # what you can filter on
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> All three tools are stubs, so that last command will do nothing useful yet.
> That's the starting position.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     This is your submission. Fill each section in as you finish the milestone
     it belongs to — don't leave it all to the end.

     Unit 3 asks for the first five sections. Unit 4 adds the five below them.
     Leave the unit 4 sections alone until then; they're here so you know
     what's coming.

     Everything is pasted as TEXT. No screenshots, no images, no video links.
     A typed block of output gets full credit; a picture of the same output
     gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 3 — THE BUILD ═══════════════════════ -->

## What This Does

<!-- Three or four sentences: what a user asks for, and what they get back. -->

A user types what they're looking for in plain words, like 'vintage graphic tee under $30' or '90s track jacket in size M'. FitFindr pulls the description, size and price ceiling out of the query and searches 40 secondhand listings from Depop, thredUp and Poshmark for the best match. It then asks Gemini for one or two outfits that pair the find with clothes the user already owns, and writes a short caption they could post. If nothing matches, it stops before the outfit step and tells the user what to change (raise the price, drop the size, or use a more common word).

---

## Tool Inventory

<!-- Four lines per tool. This is worth 2 points and it's the single most
     common place students lose them.

     "Returns a list" earns NOTHING. The description has to say what is IN
     the list.

     The empty case isn't optional either — it's the thing your loop branches
     on, and if you don't decide it here you'll discover it as a crash in
     Milestone 5. -->

### `search_listings`

- **What it does:** Filters the listings by price and size, scores what's left by how many description words each listing contains, and returns the best matches first.
- **Inputs:**
  - `description` (str) — keywords like "vintage graphic tee". Searched in: title, description, category and style_tags. Case-insensitive. Null fields (like brand) are skipped. These words are ignored: a, an, the, in, of, with, for, and, or, to, on, my, i, im, looking, want, need, some, something.
  - `size` (str or None) — e.g. "M". Split the listing’s size on /, spaces and parentheses; it matches if one piece equals the user’s size (ignoring case). "One Size" listings match any size. None means no size filter.
  - `max_price` (float or None) — keeps listings with price ≤ max_price. None means no price filter.
- **Returns:** a list of up to 10 listing dicts (all fields: id, title, description, category, style_tags, size, condition, price, colors, brand, platform), sorted by score highest first. Score = the number of query words found in the searched fields (repetition of a word doesn't count). Ties keep original file order.
- **When it has nothing:** an empty list `[]` — never None, never an error.

### `suggest_outfit`

- **What it does:** Asks the model for one or two outfits built around the new item, using pieces from the user's wardrobe.
- **Inputs:** `new_item` (dict) — one listing dict from search_listings. `wardrobe` (dict) — `{"items": [...]}`, each item with id, name, category, colors, style_tags, notes.
- **Returns:** a non-empty string with 1–2 outfit suggestions that name specific wardrobe items by name.
- **When it has nothing:** if `wardrobe["items"]` is empty, it returns general styling advice for the item (still a non-empty string) — never "" and never an error.

### `create_fit_card`

- **What it does:** Asks the model for a short social-media caption about the find and the outfit.
- **Inputs:** `outfit` (str) — the string from suggest_outfit. `new_item` (dict) — the same listing dict.
- **Returns:** a 2–4 sentence caption string that mentions the item, its price and its platform once each.
- **When it has nothing:** if `outfit` is empty or only whitespace, it returns the message "Can't write a fit card: no outfit suggestion was given." — no model call, no error.

---

## Planning Loop

<!-- Your branch rule, stated as a rule — the condition AND both paths — plus
     the file and function that holds it.

     Like this:
       "If search_listings returns an empty list, put a message in the session
        and stop. Otherwise take the first result and go to suggest_outfit."
        — agent.py::run_agent

     The grader checks your code against what you claim here, so the file and
     function have to be real. -->

**Branch rule:**

If search_listings returns an empty list, put a message in session["error"] that says nothing matched and suggests what to change (raise the max price, drop or change the size, or use different words), then stop without calling suggest_outfit. Otherwise, save the first result to session["selected_item"], pass it to suggest_outfit, save that to session["outfit_suggestion"], then pass both to create_fit_card and save the result to session["fit_card"].

**Where it lives:** `agent.py::run_agent`

**How the query is parsed:** <!-- regex, string splitting, or asking the model — say which -->

Regex in agent.py::parse_query. max_price is the number after "under", "below", "less than", "max", "up to" or "$". size is the word after "size". description is what's left, with "looking for", "i want", "i need" and "show me" removed.

**What moves through the session:** <!-- which fields, in what order -->

What moves through the session: run_agent stores every result in the session dict and reads the next tool's inputs back out of it. session["parsed"] (description, size, max_price) feeds search_listings; its list goes in session["search_results"]; the first result is copied to session["selected_item"], which is what suggest_outfit receives along with session["wardrobe"]; its text goes in session["outfit_suggestion"], which create_fit_card receives with the same selected_item; the caption goes in session["fit_card"]. On the empty branch, session["error"] gets the message and the later fields stay None.

---

## Sample Run

<!-- Two things go here.

     1. One FULL query and its output, pasted as text.
     2. Your three per-tool terminal tests — the command and what it printed. -->

$ python app.py ask 'vintage graphic tee under $30'

  Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop

  Outfit:   Grab this tee! It is a total steal and will look amazing with your current pieces.

Outfit 1: Casual Street
Pair the Y2K Baby Tee with your baggy straight-leg jeans, dark wash. Throw on the vintage black denim jacket and finish with chunky white sneakers and the black crossbody bag for an effortless 2000s look.

Outfit 2: Y2K Contrast
Tuck the Y2K Baby Tee into your wide-leg khaki trousers. Layer the black cropped zip hoodie right over top, left unzipped to show the butterfly print. Add the black combat boots to ground the soft pastel colors.

  Fit card: Found this adorable butterfly baby tee for just $18.0 and I am obsessed with the early 2000s energy. It is so easy to dress down with baggy denim or toughen up with combat boots and a zip hoodie. Snag it on my depop before I change my mind and keep it.

#y2kstyle #babytee #depopshop

0 model calls this session, 2 served from cache

=== A query it can't ===
  stopped: No listings matched 'designer ballgown' in size XXS under $5. Try: raise your max price above $5; drop the size or try a size next to XXS; use a more common word for the item (e.g. 'dress', 'jacket', 'tee', 'jeans').
  fit_card is None - it should still be None here

$ python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"
[{'id': 'lst_002', 'title': 'Y2K Baby Tee — Butterfly Print', 'description': 'Super cute early 2000s baby tee with butterfly graphic. Fitted crop length. Tag says medium but fits like a small.', 'category': 'tops', 'style_tags': ['y2k', 'vintage', 'graphic tee', 'cottagecore'], 'size': 'S/M', 'condition': 'excellent', 'price': 18.0, 'colors': ['white', 'pink', 'purple'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_006', 'title': 'Graphic Tee — 2003 Tour Bootleg Style', 'description': 'Vintage-style bootleg tee with faded graphic. Slightly boxy fit. 100% cotton, soft and worn-in.', 'category': 'tops', 'style_tags': ['graphic tee', 'vintage', 'grunge', 'streetwear', 'band tee'], 'size': 'L', 'condition': 'good', 'price': 24.0, 'colors': ['black'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_017', 'title': 'Mesh Long-Sleeve Top — Black', 'description': 'Sheer black mesh long-sleeve. Great for layering under a graphic tee or over a bralette. Stretchy material, fits true to size.', 'category': 'tops', 'style_tags': ['y2k', 'grunge', 'goth', 'layering'], 'size': 'S/M', 'condition': 'excellent', 'price': 15.0, 'colors': ['black'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_033', 'title': 'Vintage Band Tee — Faded Grey', 'description': 'Faded grey band-style tee with distressed graphic. Crew neck. Fits boxy. Well-loved but no holes or major damage.', 'category': 'tops', 'style_tags': ['vintage', 'grunge', 'band tee', 'graphic tee', 'streetwear'], 'size': 'L', 'condition': 'fair', 'price': 19.0, 'colors': ['grey', 'charcoal'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_011', 'title': 'Low-Rise Cargo Pants — Khaki', 'description': 'Y2K era low-rise cargo pants. Lots of pockets. Khaki color, slightly distressed at the hems. Great for layering with a long tee.', 'category': 'bottoms', 'style_tags': ['y2k', 'cargo', '2000s', 'streetwear'], 'size': 'W29', 'condition': 'fair', 'price': 27.0, 'colors': ['khaki', 'tan'], 'brand': None, 'platform': 'poshmark'}, {'id': 'lst_015', 'title': 'Vintage Graphic Hoodie — Faded Black', 'description': 'Faded black pullover hoodie with barely-visible vintage graphic on the chest. Cozy interior. Some pilling but adds to the worn-in look.', 'category': 'tops', 'style_tags': ['vintage', 'grunge', 'graphic', 'streetwear'], 'size': 'L', 'condition': 'fair', 'price': 26.0, 'colors': ['black', 'charcoal'], 'brand': None, 'platform': 'depop'}]

$ python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
Grab those Levi's—they are a thrift store holy grail! Since your dark jeans are baggy and high-waisted, these 501s will give you that classic, straight-leg vintage fit.

Outfit one: tuck your white ribbed tank top into the vintage Levi's 501 Jeans — Medium Wash, add the brown leather belt, and finish with the chunky white sneakers and black crossbody bag for an effortless 90s look.

Outfit two: layer the oversized grey crewneck sweatshirt over the vintage Levi's 501 Jeans — Medium Wash, and pair them with your black combat boots for a cozy, streetwear-inspired vibe. At thirty-eight dollars, they're an absolute steal!

$ python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"
Nothing beats a broken-in pair of vintage Levi's 501 jeans for that effortless 90s off-duty look. I'm styling these with crisp white sneakers for the ultimate casual weekend fit. Grab this medium wash staple for just $38 over on my Depop before I change my mind and keep them.

```

---

## How I Used AI

<!-- Two specific moments. What you asked, what came back, what you changed.

     "I used Claude to help me code" is not enough.

     "I gave Claude my search_listings spec. It returned None on no match
     instead of an empty list, so I changed it" is the level we want. -->

**Moment 1**

- *What I asked for:* I provided Claude with my first size rule for search_listings i.e., a listing matches when an exact match is present, and then I asked whether this can be built from spec.
- *What came back:* It let me know that the rule was not specific enough i.e., would M count as present in S/M? Additionally, I thought that would neglect One Size listings.
- *What I changed:* I rewrote the rule to be more specific and split the listings' size on /, space and parantheses. Additionally, I created the rule that One Size matches any size.

**Moment 2**

- *What I asked for:* I asked Claude to check my reasoning from criterion 1, which was that a wardrobe that doesn't go with the item could stop the fit card.
- *What came back:* It pointed out that a mismatched wardrobe would simply return a bad fit card and would still return a fit card. 
- *What I changed:* This made me reflect on each step in the pipeline and I rewrote my reason to be due to failing AI calls instead.

<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

<!-- Five criteria, five tries each, in this exact format.

     Five, because your criteria are written out of five. Mark each try PASS
     or FAIL, count the passes, and read that count against your target — a
     row targeting 4 of 5 with three PASS cells is MISSED (3/5).

     `python run_eval.py --label before` runs everything and writes the table
     into results/. Paste it here and fill in the verdicts. -->

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Real output from one try**, pasted as text, naming the file and function
that produced it:

```

```

---

## Verdicts and Diagnoses

<!-- MET or MISSED per criterion against LAST UNIT's target, plus a sentence on
     how you decided.

     Then, for every miss: which of the four places it happened — a tool, the
     loop's branch, the session, or the model's output — AND the mechanism.

     Not a diagnosis:  "The fit card was bad."
     A diagnosis:      "The fit card criterion missed on 2 of 5 items. Both had
                        an empty brand field. My prompt puts the brand in the
                        first sentence, so the card opened with a blank and read
                        like a fragment. The tool worked; the prompt assumed a
                        field that isn't always there."

     Look for a pattern. Three misses on the same tool is one problem, not
     three. -->

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 |  |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |
| 4 |  |  |  |  |
| 5 |  |  |  |  |

**Diagnoses**



---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

**Happy path**

```

```

**Empty search**

```

```

**On the MCP move:** <!-- what changed in your code, and whether anything
behaved differently afterwards. If the rewire didn't work, say exactly where it
broke — the error text and the last thing that worked. That earns the point in
full. -->



---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:**

**Which failure it was meant to fix:**

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Did it help, and how do I know:**

<!-- If it made things worse, say that. Honestly reported, that earns full
     credit and is more interesting than one that worked. -->



---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped where
     you did. "I ran out of time" is fine if it's true. Pretending nothing is
     left is not. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 3

       [ ] criteria.md has five numbered criteria, each with a target
       [ ] Each criterion has a reason underneath it
       [ ] All five unit 3 sections above have real content
       [ ] Tool Inventory: all three tools, inputs WITH TYPES, a specific
           return value, and the empty case
       [ ] Planning Loop names the branch rule and agent.py::run_agent
       [ ] Sample Run: one full query plus the three per-tool tests, as text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN, you submit the same one
           next unit

     SUBMISSION CHECKLIST — unit 4

       [ ] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [ ] Run Log — Before, five criteria, five tries each
       [ ] Real output pasted underneath, naming file and function
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, naming a place AND a mechanism
       [ ] Loop Trace, with the MCP call visible in it
       [ ] All three failure modes triggered and handled
       [ ] One improvement, with Run Log — After in the same format
       [ ] What's Still Broken
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
