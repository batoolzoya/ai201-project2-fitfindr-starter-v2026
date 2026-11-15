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

Regex in agent.py::parse_query. max_price is the number after "under", "below", "less than", "max", "up to" or "$". size is the word aft-*4333333333333333333333333333333333333333333er "size". description is what's left, with "looking for", "i want", "i need" and "show me" removed.

**What moves through the session:** <!-- which fields, in what order -->

run_agent stores every result in the session dict and reads the next tool's inputs back out of it. session["parsed"] (description, size, max_price) feeds search_listings; its list goes in session["search_results"]; the first result is copied to session["selected_item"], which is what suggest_outfit receives along with session["wardrobe"]; its text goes in session["outfit_suggestion"], which create_fit_card receives with the same selected_item; the caption goes in session["fit_card"]. On the empty branch, session["error"] gets the message and the later fields stay None.

---

## Sample Run

<!-- Two things go here.

     1. One FULL query and its output, pasted as text.
     2. Your three per-tool terminal tests — the command and what it printed. -->

```

$ python app.py ask 'vintage graphic tee under $30'

```

  Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop

  Outfit:   Grab this tee! It is a total steal and will look amazing with your current pieces.

Outfit 1: Casual Street
Pair the Y2K Baby Tee with your baggy straight-leg jeans, dark wash. Throw on the vintage black denim jacket and finish with chunky white sneakers and the black crossbody bag for an effortless 2000s look.

Outfit 2: Y2K Contrast
Tuck the Y2K Baby Tee into your wide-leg khaki trousers. Layer the black cropped zip hoodie right over top, left unzipped to show the butterfly print. Add the black combat boots to ground the soft pastel colors.

  Fit card: Found this adorable butterfly baby tee for just $18.0 and I am obsessed with the early 2000s energy. It is so easy to dress down with baggy denim or toughen up with combat boots and a zip hoodie. Snag it on my depop before I change my mind and keep it.

#y2kstyle #babytee #depopshop

0 model calls this session, 2 served from cache


```

=== A query it can't ===

```
  stopped: No listings matched 'designer ballgown' in size XXS under $5. Try: raise your max price above $5; drop the size or try a size next to XXS; use a more common word for the item (e.g. 'dress', 'jacket', 'tee', 'jeans').
  fit_card is None - it should still be None here


```

$ python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"

```

[{'id': 'lst_002', 'title': 'Y2K Baby Tee — Butterfly Print', 'description': 'Super cute early 2000s baby tee with butterfly graphic. Fitted crop length. Tag says medium but fits like a small.', 'category': 'tops', 'style_tags': ['y2k', 'vintage', 'graphic tee', 'cottagecore'], 'size': 'S/M', 'condition': 'excellent', 'price': 18.0, 'colors': ['white', 'pink', 'purple'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_006', 'title': 'Graphic Tee — 2003 Tour Bootleg Style', 'description': 'Vintage-style bootleg tee with faded graphic. Slightly boxy fit. 100% cotton, soft and worn-in.', 'category': 'tops', 'style_tags': ['graphic tee', 'vintage', 'grunge', 'streetwear', 'band tee'], 'size': 'L', 'condition': 'good', 'price': 24.0, 'colors': ['black'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_017', 'title': 'Mesh Long-Sleeve Top — Black', 'description': 'Sheer black mesh long-sleeve. Great for layering under a graphic tee or over a bralette. Stretchy material, fits true to size.', 'category': 'tops', 'style_tags': ['y2k', 'grunge', 'goth', 'layering'], 'size': 'S/M', 'condition': 'excellent', 'price': 15.0, 'colors': ['black'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_033', 'title': 'Vintage Band Tee — Faded Grey', 'description': 'Faded grey band-style tee with distressed graphic. Crew neck. Fits boxy. Well-loved but no holes or major damage.', 'category': 'tops', 'style_tags': ['vintage', 'grunge', 'band tee', 'graphic tee', 'streetwear'], 'size': 'L', 'condition': 'fair', 'price': 19.0, 'colors': ['grey', 'charcoal'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_011', 'title': 'Low-Rise Cargo Pants — Khaki', 'description': 'Y2K era low-rise cargo pants. Lots of pockets. Khaki color, slightly distressed at the hems. Great for layering with a long tee.', 'category': 'bottoms', 'style_tags': ['y2k', 'cargo', '2000s', 'streetwear'], 'size': 'W29', 'condition': 'fair', 'price': 27.0, 'colors': ['khaki', 'tan'], 'brand': None, 'platform': 'poshmark'}, {'id': 'lst_015', 'title': 'Vintage Graphic Hoodie — Faded Black', 'description': 'Faded black pullover hoodie with barely-visible vintage graphic on the chest. Cozy interior. Some pilling but adds to the worn-in look.', 'category': 'tops', 'style_tags': ['vintage', 'grunge', 'graphic', 'streetwear'], 'size': 'L', 'condition': 'fair', 'price': 26.0, 'colors': ['black', 'charcoal'], 'brand': None, 'platform': 'depop'}]

```

$ python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"

```

Grab those Levi's—they are a thrift store holy grail! Since your dark jeans are baggy and high-waisted, these 501s will give you that classic, straight-leg vintage fit.

Outfit one: tuck your white ribbed tank top into the vintage Levi's 501 Jeans — Medium Wash, add the brown leather belt, and finish with the chunky white sneakers and black crossbody bag for an effortless 90s look.

Outfit two: layer the oversized grey crewneck sweatshirt over the vintage Levi's 501 Jeans — Medium Wash, and pair them with your black combat boots for a cozy, streetwear-inspired vibe. At thirty-eight dollars, they're an absolute steal!

```

$ python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"

```

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

**Moment 3 (unit 4)**

- *What I asked for:* I gave Claude my before run log and asked it to call each criterion against my targets and find the cause of each miss.
- *What came back:* It marked criterion 4 MISSED 0/5, because no card used the exact title, and showed that both criterion 5 misses had the same cause: a query word not in the data, a 1-point tie, and file order picking the wrong listing.
- *What I changed:* I picked one improvement, the fit card prompt, because it was the bigger miss and the diagnosis pointed straight at one line. I left search for What's Still Broken rather than changing two things at once.


<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. Matching query completes all three tools | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. Impossible query stops before suggest_outfit, names what to change | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. search_results[0] id = selected_item id = id passed to suggest_outfit | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. Fit card: 2–4 sentences, item title, price, platform once each | 4 of 5 | FAIL | FAIL | FAIL | FAIL | FAIL | MISSED (0/5) |
| 5. Differently-worded queries put an expected listing first | 4 of 5 | FAIL | PASS | FAIL | PASS | PASS | MISSED (3/5) |

Criteria 1–4: `python run_eval.py --label before` (file: `results/run_..._before.md`, produced by `run_eval.py::main`, loop `agent.py::run_agent`). Criterion 5 is about search alone (plain code, no model), so its 5 tries are the 5 queries in criteria.md, run through MCP by `check_search.py`. Empty wardrobe was also run 5 times as a diagnostic (5/5 returned general advice, no crash).

**Real output from one try per criterion**

Criterion 1 — `agent.py::run_agent`, scenario "matching query completes", Try 1:

```
- stopped early: no
- selected_item: Y2K Baby Tee — Butterfly Print ($18.0, depop)
Fit card:
Found the ultimate Y2K butterfly baby tee and I am obsessed with the nostalgic print. I've got it listed on depop for $18.0 so you can channel your inner 2000s pop star all summer. It looks so good with baggy denim or toughened up with combat boots. #y2kfashion #babytee #thriftootd
```

Criterion 2 — `agent.py::run_agent`, scenario "impossible query stops early", Try 1:

```
- stopped early: yes — No listings matched 'designer ballgown' in size XXS under $5. Try: raise your max price above $5; drop the size or try a size next to XXS; use a more common word for the item (e.g. 'dress', 'jacket', 'tee', 'jeans').
- selected_item: (none)
- search_results: 0
[2] search_listings (via MCP)
      in:  description='designer ballgown', size=XXS, max_price=5.0
      out: [] (empty)
      →    branch: empty list -> stop, suggest_outfit is NOT called
```

Criterion 3 — `agent.py::run_agent` trace, scenario "selected item is the item passed on", Try 1:

```
[2] search_listings (via MCP)
      →    branch: 10 results -> continue; search_results[0] id=lst_002
[3] select_item
      in:  search_results[0]
      out: selected_item id=lst_002 - Y2K Baby Tee — Butterfly Print
[4] suggest_outfit
      in:  new_item id=lst_002, wardrobe: 10 items
```

Criterion 4 — `tools.py::create_fit_card`, scenario "fit card content", Try 1 (FAIL: says "butterfly baby tee", not the title "Y2K Baby Tee — Butterfly Print"):

```
Absolute peak early 2000s energy with this butterfly baby tee, and it’s giving major nostalgic mall-rat vibes. Grabbed it for just $18.0 over on depop before I hoard all the pastel graphics for myself.

#y2k #babytee #depopshop
```

Criterion 5 — `check_search.py` (calls `search_listings` via MCP):

```
Try 1: 'jean jacket'
   expected: lst_007
   first:    lst_004 - 90s Track Jacket — Navy/White Stripe
   top 3:    lst_004, lst_007, lst_022
   -> FAIL
Try 2: 'graphic t-shirt'
   expected: lst_002 or lst_006 or lst_033
   first:    lst_002 - Y2K Baby Tee — Butterfly Print
   -> PASS
Try 3: 'band shirt under $25'
   expected: lst_033 or lst_006
   first:    lst_003 - Oversized Flannel Shirt — Plaid Red/Black
   top 3:    lst_003, lst_006, lst_024
   -> FAIL
Try 4: 'chunky knit sweater'
   expected: lst_008
   first:    lst_008 - Knit Cardigan — Chunky Brown
   -> PASS
Try 5: 'leather jacket'
   expected: lst_022
   first:    lst_022 - 90s Leather Bomber — Black
   -> PASS
3 of 5 passed
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
| 1 | Matching query completes all three tools | 4 of 5 | MET (5/5) | All 5 tries had a fit card and no early stop. |
| 2 | Impossible query stops before suggest_outfit | 5 of 5 | MET (5/5) | All 5 traces end at step 2 with "suggest_outfit is NOT called", fit_card None, and a message listing three things to change. |
| 3 | Selected item is the item passed on | 5 of 5 | MET (5/5) | In every trace, search_results[0], selected_item and the new_item passed to suggest_outfit are all lst_002. |
| 4 | Fit card content | 4 of 5 | MISSED (0/5) | All 5 cards were 2–3 sentences (hashtags not counted) with the price and platform once each, but none contained the item title "Y2K Baby Tee — Butterfly Print". My criterion says title, so each try fails. |
| 5 | Differently-worded queries | 4 of 5 | MISSED (3/5) | 'jean jacket' and 'band shirt under $25' put a wrong listing first. |

**Diagnoses**

**Criterion 4 — the model's output (prompt in `tools.py::create_fit_card`).** It missed on 5 of 5. Every card names the item in casual words ("butterfly baby tee", "Y2K butterfly tee") instead of the listing title. The prompt passes the title in but only says "Mention the item, the price and the platform exactly once each" — it never asks for the title word for word, and a listing title with an em dash ("Y2K Baby Tee — Butterfly Print") doesn't read like something a person would post, so the model paraphrases it every time. The tool, branch and session all worked; the prompt didn't ask for what my criterion checks. Price and platform passed on all 5, so the problem is only the title.

**Criterion 5 — the search tool (`tools.py::search_listings`).** Both misses have the same mechanism, so it's one problem. Search counts whole words exactly. In 'jean jacket', "jean" appears in no listing ("jeans" is a different word), so every listing with "jacket" scores 1 — four listings tie, ties keep file order, and lst_004 (Track Jacket) comes before lst_007 (Denim Jacket). In 'band shirt under $25', "shirt" matches the Flannel Shirt and "band" matches the two band tees, all at score 1, and the flannel (lst_003) comes first in the file. Pattern: when a query word isn't in the data's vocabulary, the right item can't outscore others and file order decides.

Pattern across all five: the plain-code parts (branch, session, criteria 2 and 3) were perfect, as predicted. Both misses came from words — the model's wording (4) and the user's wording (5).

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
$ python app.py ask 'vintage graphic tee under $30' --trace
[1] parse_query
      in:  vintage graphic tee under $30
      out: description='vintage graphic tee', size=None, max_price=30.0
[2] search_listings (via MCP)
      in:  description='vintage graphic tee', size=None, max_price=30.0
      out: 10 items: Y2K Baby Tee — Butterfly Print, Graphic Tee — 2003 Tour Bootleg Style, Vintage Band Tee — Faded Grey … +7 more
      →    branch: 10 results -> continue; search_results[0] id=lst_002
[3] select_item
      in:  search_results[0]
      out: selected_item id=lst_002 - Y2K Baby Tee — Butterfly Print
[4] suggest_outfit
      in:  new_item id=lst_002, wardrobe: 10 items
      out: Grab this tee! It is a total steal and will look amazing with your current pieces.   Outfit 1: Casual Street P…
[5] create_fit_card
      in:  outfit (549 chars), new_item id=lst_002
      out: Found this adorable butterfly baby tee for just $18.0 and I am obsessed with the early 2000s energy. It is so …
```
```

**Empty search**

```
```
$ python app.py ask 'designer ballgown size XXS under $5' --trace
[1] parse_query
      in:  designer ballgown size XXS under $5
      out: description='designer ballgown', size=XXS, max_price=5.0
[2] search_listings (via MCP)
      in:  description='designer ballgown', size=XXS, max_price=5.0
      out: [] (empty)
      →    branch: empty list -> stop, suggest_outfit is NOT called

  No listings matched 'designer ballgown' in size XXS under $5. Try: raise your max price above $5; drop the size or try a size next to XXS; use a more common word for the item (e.g. 'dress', 'jacket', 'tee', 'jeans').
```
**Failure modes, triggered on purpose:**

Empty wardrobe (`python app.py ask 'denim jacket under $50' --empty-wardrobe`) — suggest_outfit got 0 items and returned general advice, no crash:

```
[4] suggest_outfit
      in:  new_item id=lst_007, wardrobe: 0 items
      out: Hey there! Grab that cropped light-wash jacket—it is a total wardrobe MVP.   For an easy everyday look, layer …
```

Model unavailable (one character of the key changed, `python app.py ask 'chelsea boots'`) — new handler in `agent.py::run_agent` catches `ModelUnavailable`:

```
[4] suggest_outfit
      in:  new_item id=lst_028, wardrobe: 10 items
      →    model unreachable -> stop

  Found Suede Chelsea Boots — Tan ($44.0 on poshmark), but couldn't reach the AI model to suggest an outfit or write a fit card. Reason: The model rejected your API key. Check GEMINI_API_KEY in your .env file, or create a fresh key at aistudio.google.com. Once that's fixed, run the same query again.
```

Empty search: see the trace above.


```

**On the MCP move:** <!-- what changed in your code, and whether anything
behaved differently afterwards. If the rewire didn't work, say exactly where it
broke — the error text and the last thing that worked. That earns the point in
full. -->

search_listings is registered in `mcp_server.py` with a description written for an outside agent (units, the size rule, and the empty case `[]`). In `agent.py::run_agent` the direct call was replaced with `mcp_client.call_tool("search_listings", {...})`, and an `MCPError` handler stops the run with a message if the server can't be reached. Nothing behaved differently: the same queries returned the same listings in the same order (the graphic tee query still picks lst_002 first), and the empty search still returns `[]`, so the branch works unchanged. The only visible difference is that each search now starts the server, which adds a moment per run.

---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:**

One line of the prompt in `tools.py::create_fit_card`. Before, it said "Mention the item, the price and the platform exactly once each." Now it says "Use the item's exact title, '<title>', word for word, exactly once. Mention the price and the platform exactly once each." Nothing else changed (search, loop, session and the other prompt are the same).

**Which failure it was meant to fix:**

Criterion 4, which missed 0/5 in the before run. My diagnosis was that the prompt never asked for the title word for word, so the model paraphrased it ("butterfly baby tee") every time. Price and platform already passed, so the title was the only thing to fix.

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. Matching query completes all three tools | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. Impossible query stops before suggest_outfit, names what to change | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. search_results[0] id = selected_item id = id passed to suggest_outfit | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. Fit card: 2–4 sentences, item title, price, platform once each | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 5. Differently-worded queries put an expected listing first | 4 of 5 | FAIL | PASS | FAIL | PASS | PASS | MISSED (3/5) |

From `python run_eval.py --label after` (`results/run_..._after.md`) and `python check_search.py`.

Criterion 4, after — `tools.py::create_fit_card`, scenario "fit card content", Try 1:

```
Found the ultimate Y2K Baby Tee — Butterfly Print and I'm obsessed with this nostalgic early 2000s energy. It's up on my Depop right now for $18.0, ready for you to style with baggy denim or wide-leg trousers.

#y2k #thrifted #babytee
```

**Did it help, and how do I know:**

Yes, for the criterion it targeted. Criterion 4 went from 0/5 to 5/5: all five "fit card content" cards contain "Y2K Baby Tee — Butterfly Print" exactly, are 2–3 sentences (hashtags not counted, same rule as the before run), and mention the price and platform once each. The other criteria didn't move — 1, 2 and 3 stayed 5/5 and 5 stayed 3/5 — which is what I'd expect from a change that only touched the fit card prompt. One side effect: with the exact title forced in, some captions read more like a listing than a post (e.g. "Every closet needs a good Denim Jacket — Light Wash, Cropped" from the empty-wardrobe runs).


---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped where
     you did. "I ran out of time" is fine if it's true. Pretending nothing is
     left is not. -->

**Criterion 5 (search wording) — still MISSED, 3/5.** I didn't touch search, because the unit allows one improvement and criterion 4 was the bigger miss (0/5). The cause is that search only counts exact words: "jean" and "shirt" never appear in the right listings, so the right item ties with others at 1 point and file order decides. What I'd do next: add a small synonym list in `tools.py::search_listings` before scoring (jean→denim, shirt/t-shirt→tee, sweater→knit), and break ties by matches in the title rather than file order. I'd then re-run `check_search.py`, plus some new phrasings, since a synonym list built from these five queries could just be fitting the test.

**Criterion 4 may be measuring the wrong thing.** It now passes 5/5, but forcing the exact listing title makes some captions sound like product listings, which goes against what a fit card is for. If I revised it, I'd keep price and platform and change "item title" to something like "names the item's type and one detail from its title", with the original line left in place. I haven't revised it here, because it measured what I wrote and I'd rather report that.

**Not tested:** what happens when the model is slow rather than unreachable, and how the agent handles queries with two sizes or prices in them.

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
