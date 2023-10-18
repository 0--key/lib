;; No comments
(setq org-capture-templates
'(("t" "Todo" entry (file+headline "~/git/lib/org/agenda/might-do.list" "Tasks")
   "* RAW %?%i\n \n %a")
  ("i" "Idiom" entry (file+headline "~/git/lib/org/drills.org" "Idioms")
   "* COMMENT >->->:drill:\n%i")
  ;;
  ("p" "Proverb" entry (file+headline "~/git/lib/org/drills.org" "Proverbs")
   "** COMMENT ==> => >> :drill:
   :PROPERTIES:
   :DRILL_CARD_TYPE: hide1cloze
   :END:\n%?%i\n\n/%c/" :empty-lines 1)
  ;;
  ("o" "Obvious proverb" entry (file+headline "~/git/lib/org/drills.org" "Proverbs")
   "** COMMENT ==> => >> :drill:
   :PROPERTIES:
   :DRILL_CARD_TYPE: hide1cloze
   :END:\n%?%i\n\n" :empty-lines 1)
  ;;
  ("w" "Quote" entry (file+headline "~/git/lib/org/drills.org" "Quotes")
   "* COMMENT >->-> %c :drill:
   :PROPERTIES:
   :DRILL_CARD_TYPE: hide1cloze
   :END:\n%?%i\n")
  ;;
  ("e" "AnonQuote" entry (file+headline "~/git/lib/org/drills.org" "Quotes")
   "** COMMENT ==> => >> :drill:
   :PROPERTIES:
   :DRILL_CARD_TYPE: hide1cloze
   :END:\n%?%i\n\n" :empty-lines 1)
  ;;
  ("n" "Notes");; <-- prefix key for notes
("nf" "Fleeting" entry (file+headline
			"~/git/lib/org/agenda/might-do.list" "Notes")
 "* RAW %?%i")
("ni" "Initial" entry (file+headline
		       "~/git/lib/org/agenda/might-do.list" "Notes")
 "* INIT %?%i")
("np" "Pythonic" entry (file+headline
		       "~/git/lib/org/agenda/py-genda.list" "Notes")
 "* INIT %?%i")
("nc" "Clocked" item (clock) "%i%?" :immediate-finish 1)

;; ‘%k’ Title of the currently clocked task.
))

 
