;; No comments
(setq org-capture-templates
      '(;; A new and raw task into initial agenda file
	("t" "Todo" entry (file+headline
			   "~/git/lib/org/agenda/might-do.list" "Tasks")
	 "* RAW %?%i\n \n %a")
	;;
	("i" "Idiom" entry (file+headline
			    "~/git/lib/org/drills.org" "Idioms")
	 "* COMMENT >->->:drill:\n%i")
	;;
	("p" "Proverb" entry (file+headline
			      "~/git/lib/org/drills.org" "Proverbs")
	 "** COMMENT ==> => >> :drill:
   :PROPERTIES:
   :DRILL_CARD_TYPE: hide1cloze
   :END:\n%?%i\n\n/%c/" :empty-lines 1)
	;;
	("o" "Obvious proverb" entry (file+headline
				      "~/git/lib/org/drills.org" "Proverbs")
	 "** COMMENT ==> => >> :drill:
   :PROPERTIES:
   :DRILL_CARD_TYPE: hide1cloze
   :END:\n%?%i\n\n" :empty-lines 1)
	;;
	("w" "Quote" entry (file+headline
			    "~/git/lib/org/drills.org" "Quotes")
	 "* COMMENT >->-> %c :drill:
   :PROPERTIES:
   :DRILL_CARD_TYPE: hide1cloze
   :END:\n%?%i\n")
	;;
	("e" "AnonQuote" entry (file+headline
				"~/git/lib/org/drills.org" "Quotes")
	 "** COMMENT ==> => >> :drill:
   :PROPERTIES:
   :DRILL_CARD_TYPE: hide1cloze
   :END:\n%?%i\n\n" :empty-lines 1)
	;;
	;;
	("n" "Notes");; <-- prefix key for notes
	;; For the crude notes only:
	("nf" "Fleeting" entry (file+headline
			"~/git/lib/org/agenda/might-do.list" "Notes")
	 "* RAW %?%i"
	 :immediate-finish 1
	 :empty-lines-after 1)
	;;
	("ni" "Initial" entry (file+headline
		       "~/git/lib/org/agenda/might-do.list" "Notes")
	 "* INIT %i%?\nSCHEDULED: %t\n"
	 :immediate-finish 1
	 :empty-lines-after 1)
	("np" "Pythonic" entry (file+headline
			"~/git/lib/org/agenda/py-genda.list" "Notes")
	 "* INIT %i%?\nSCHEDULED: %t\n"
	 :immediate-finish 1
	 :empty-lines-after 1)
	;;
;; Section for advanced note-taking currently clocked tasks
	;;
	("c" "Clocked");; <-- prefix key for current task	
	;; Just plain text item note without any interruption:
	("cc" "Clocked-snippet" item (clock) "%i %U" :immediate-finish 1)
	("cl" "Clocked-link-only" item (clock) "%l %U" :immediate-finish 1)
;;
;; The offspring birth from the parent item
	("co" "Child" entry (clock)
	 "* INIT %i\nSCHEDULED: %t\n%l%?\n%U"
	 :empty-lines-after 1)
))

 
