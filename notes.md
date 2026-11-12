\# Data notes (Milestone 1)



\## Listing fields

\- Fields on every listing: id (str), title (str), description (str), category (str), style\_tags (list), size (str), condition (str), price (float), colors (list), brand (str, sometimes null), platform (str).

\- Fields search\_listings can filter on:

&#x20; - description -> I'll search these fields: title, description, category, style\_tags, condition, colors, brand

&#x20; - size -> the "size" field (it's text, not a number)

&#x20; - max\_price -> the "price" field (it's a number)



\## Wardrobe

\- A wardrobe looks like: A dictionary with one key, "items" containing a list that contains subdictionaries with the keys: id (str), name (str), category (str), colors (list), style\_tags (list), notes (str)

\- An empty wardrobe looks like: {"items": \[]} i.e., the list is empty

\- Fields that can be null: notes



\## Things that can be tricky

\- Sizes are written inconsistently. For example, we have One Size, M and M/L, which will all work for someone who wears medium. However, there is also US size 9, W30 L30 and larger sizes with notes they run small. 

\- Vintage is a keyword that appears in almost all listings so the criteria cannot be focused on only one keyword match

\- Description can appear in a different field such as "graphic tee" showing up in style\_tags so you have to make sure to check the full listing

\- There are errors in the data such as a slip dress appearing under "bottoms"

