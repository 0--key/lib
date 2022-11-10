;; sudo chown <username> /etc/emacs/site-start.d/00debian.el
(tool-bar-mode -1)
(menu-bar-mode -1)
(scroll-bar-mode -1)
;; (desktop-save-mode 1) ;; temporary !!

;; 55.04665127097639, -7.565092591636581
;; Baile Uí Fhloinn
(setq calendar-latitude 55.0466)
   (setq calendar-longitude -7.5651)
   (setq calendar-location-name "Baile Uí Fhloinn, Co. Donegal")
;; (setq calendar-latitude 47.5)
;;    (setq calendar-longitude 34.65)
;;    (setq calendar-location-name "Energodar, ZP")


(require 'package)
;; New 2022 Year and dances with drums around org replacement
;;(add-to-list 'package-archives '("org" . "http://orgmode.org/elpa/") t)
(add-to-list 'package-archives '("elpa" . "https://elpa.gnu.org/packages/") t)
;; and MELPA
(add-to-list 'package-archives '("melpa" . "https://melpa.org/packages/") t)

(package-initialize)

(setq gnutls-algorithm-priority "NORMAL:-VERS-TLS1.3") ;; Bad request fix

(load-theme 'wombat)

(require 'org)
(require 'org-tempo)
(require 'org-bullets)
;;(require 'go-mode)
(require 'ob-go)

(add-hook 'org-mode-hook (lambda () (org-bullets-mode 1)))

(require 'key-chord)
(key-chord-mode 1)
;; KeyChords are below
;; Chords for full-fledged keyboard
(key-chord-define-global "'\\"     'other-frame)
(key-chord-define-global "]\\"     'other-frame)
(key-chord-define-global "';"     'other-frame)
(key-chord-define-global "bn"     'list-buffers)
(key-chord-define-global "bv"     'switch-to-buffer)
(key-chord-define-global "ew"     'eval-last-sexp)
(key-chord-define-global "fd"     'previous-buffer)
(key-chord-define-global "kj"     'next-buffer)
(key-chord-define-global "q1"     'delete-other-windows)
(key-chord-define-global "w2"     'split-window-below)
(key-chord-define-global "e3"     'split-window-right)
(key-chord-define-global "sq"     'save-some-buffers)
(key-chord-define-global "fg"     'find-file)
(key-chord-define-global "jl"     'move-end-of-line)
(key-chord-define-global "fs"     'move-beginning-of-line)
(key-chord-define-global "0o"     'delete-window)
(key-chord-define-global "bk"     'kill-buffer)
;;
;; (key-chord-define-global "ri"     'insert-register) ;; too common

(require 'magit)
(key-chord-define-global "gs"     'magit-status)

(require 'google-translate)
(setq google-translate-translation-directions-alist '(("en" . "ru")))
(setq google-translate-default-source-language "en")
(setq google-translate-default-target-language "ru")
;; Minor correction for translator
(defun google-translate--search-tkk () "Search TKK." (list 430675 2721866130))

(require 'voca-builder)
(setq voca-builder/voca-file "~/git/lib/org/vocabulary/202211.org")
(setq voca-builder/export-file "~/.voca-builder-temp.org")
(setq voca-builder/current-tag "misc")
(setq voca-builder/current-tag "DarkPersuasion")
(setq voca-builder/current-tag "Elephant")
(setq voca-builder/current-tag "Zen")
(setq voca-builder/current-tag "Money")
(setq voca-builder/current-tag "Stupidity")
(setq voca-builder/current-tag "Dahl")

(key-chord-define-global "tr"     'google-translate-at-point)
(key-chord-define-global "ty"     'voca-builder/search-popup)

(add-to-list 'load-path "~/git/bookmark-plus/")
(require 'bookmark+)
;;
(key-chord-define-global "bm"     'bmkp-bookmark-set-confirm-overwrite)
(key-chord-define-global "lb"     'bookmark-bmenu-list)
(key-chord-define-global "jb"     'bookmark-jump)
;;
(key-chord-define-global "sb"     'bookmark-bmenu-save)
;;
(key-chord-define-global "vf"     'kill-ring-save)
(key-chord-define-global "rf"     'kill-region)
(key-chord-define-global "uy"     'yank)
(key-chord-define-global "oj"     'other-window)
(key-chord-define-global "ij"     'scroll-down-command)
(key-chord-define-global "nj"     'scroll-up-command)
;;
;; version-control section
(key-chord-define-global "vl"     'vc-print-log)
;;

(key-chord-define-global "hg"     'keyboard-quit)
(key-chord-define org-mode-map "km"     'org-meta-return)
(key-chord-define-global "ga"     'org-agenda)
(key-chord-define org-mode-map "a["     'org-agenda-file-to-front)
(key-chord-define org-mode-map "a]"     'org-remove-file)
(key-chord-define org-mode-map "od"     'org-deadline)
(key-chord-define org-mode-map "so"     'org-schedule)
(key-chord-define-global "ol"     'org-store-link)
(key-chord-define org-agenda-mode-map "lo"     'org-agenda-open-link)
(key-chord-define org-agenda-mode-map "-p"     'org-agenda-drag-line-forward)
(key-chord-define org-agenda-mode-map "=["     'org-agenda-drag-line-backward)

(key-chord-define org-agenda-mode-map "za"     'org-agenda-toggle-archive-tag)

(require 'dictionary)
(key-chord-define-global "wt"     'dictionary-lookup-definition)



(require 'ereader)
(require 'howdoi)
(require 'org-drill)
(require 'elpy)

(pyvenv-activate "/home/alioth/.emacs.d/py3.7.3/")

;; Programming languages for Babel

(org-babel-do-load-languages
 'org-babel-load-languages
 '((python . t)
   (emacs-lisp . t)
   (shell . t)
   (sqlite . t)
   (go . t)
   (C . t)
   )) ;; perhaps this hunk is redundant because init.el contains the
      ;; similar one in the =custom= section
;;
(global-set-key (kbd "C-c c") 'org-capture)
;;

(setq org-capture-templates
'(("p" "Todo" entry (file+headline "~/org/gtd.org" "Tasks")
   "* TODO %?\n  %i\n  %a")
  ("i" "Idiom" entry (file+headline "/home/alioth/git/lib/org/drills.org" "Idioms")
   "* >->-> :drill:\n%i")
  ;;
  ("t" "Thought" entry (file+headline "/home/alioth/git/lib/org/drills.org" "Thoughts")
   "* >->-> :drill:\n%i")
  ;;
  ("w" "Quote" entry (file+headline "/home/alioth/git/lib/org/drills.org" "Quotes")
   "* >->-> %c :drill:\n%i")
  ;;
  ("r" "Proverb riddle" entry (file+datetree "/home/alioth/git/lib/org/proverbs.org")
   "* %c\n %? %i \n %f")
  ;;
  ("o" "Proverb obvious" entry (file+datetree "/home/alioth/git/lib/org/proverbs.org")
   "* %i \n %f")
  ;; 
  ("j" "Journal" entry (file+datetree "~/org/journal.org")
   "* %?\nEntered on %U\n  %i\n  %a")
;;
  ("d" "Drill-item" entry (file+headline "/home/alioth/git/lib/org/drills.org" "Microservices")
   "* >->-> :drill:\n%i")
  ;;
  ("s" "SRE" entry (file+headline "/home/alioth/git/lib/org/drills.org" "Site Reliability Engineering")
   "* >->-> :drill:\n%i")
   ;;
   ("z" "Zettelkasten"
    plain
    (file+headline "~/git/org-pub/2022-01-26-zettelkasten.org"
		   "Notes")
    "%i\n  %a \n")
   ;;
("n" "Notes");; <-- prefix key for notes
("nf" "Fleeting" entry (file+headline
			"~/git/lib/org/agenda/might-do.list" "Notes")
 "* RAW %?%i")
("ni" "Initial" entry (file+headline
		       "~/git/lib/org/agenda/might-do.list" "Notes")
 "* INIT %?\n%i\n%l")
   ;; ‘%k’ Title of the currently clocked task.
   ))

;; Jekyll settings there -->
;;
(setq org-publish-project-alist
'(("jekyll-org"
   :base-directory "/home/alioth/git/org-pub/"
   :base-extension "org"
   ;; Path to your Jekyll project.
   :publishing-directory "/home/alioth/git/0--key.github.io/_posts/"
   :recursive t
   :publishing-function org-html-publish-to-html
   :headline-levels 4
   :html-extension "html"
   :section-numbers nil
   :with-toc nil
   :body-only t
   ;; Only export section between <body> </body> (body-only)
   )
  ("jekyll-org-img"
   :base-directory "/home/alioth/git/org-pub/img/"
   :base-extension "css\\|js\\|png\\|jpg\\|gif\\|pdf\\|mp3\\|ogg\\|swf\\|php"
   :publishing-directory "/home/alioth/git/0--key.io/assets/img/"
   :recursive t
   :publishing-function org-publish-attachment)

  ("jekyll" :components ("jekyll-org" "jekyll-org-img"))
  ))
;;


;; LangTool
(require 'langtool)
(setq langtool-language-tool-jar "/usr/local/java/LanguageTool-5.0/languagetool-commandline.jar")
(setq langtool-default-language "en-US")
    (global-set-key "\C-x4w" 'langtool-check)
    (global-set-key "\C-x4W" 'langtool-check-done)
    (global-set-key "\C-x4l" 'langtool-switch-default-language)
    (global-set-key "\C-x44" 'langtool-show-message-at-point)
    (global-set-key "\C-x4c" 'langtool-correct-buffer)
;;
;; <-- Elaboration required


;; Out of the box section
;; Set the default mail server and news server as specified by Debian
;; policy.

(setq gnus-nntpserver-file "/etc/news/server")

(setq mail-host-address (let ((name (expand-file-name "/etc/mailname")))
                          (if (not (file-readable-p name))
                              nil
                            (with-temp-buffer
                              (insert-file-contents-literally name)
                              (while (search-forward "\n" nil t)
                                (replace-match "" nil t))
                              (buffer-string)))))
