;; sudo chown <username> /etc/emacs/site-start.d/00debian.el
(tool-bar-mode -1)
(menu-bar-mode -1)
(scroll-bar-mode -1)
;; (desktop-save-mode 1) ;; temporary !!

   (setq calendar-latitude 47.5)
   (setq calendar-longitude 34.65)
   (setq calendar-location-name "Energodar, ZP")


(require 'package)
(add-to-list 'package-archives '("org" . "http://orgmode.org/elpa/") t)
;; and MELPA
(add-to-list 'package-archives '("melpa" . "https://melpa.org/packages/") t)
(package-initialize)
(setq gnutls-algorithm-priority "NORMAL:-VERS-TLS1.3") ;; Bad request fix

(load-theme 'wombat)

(require 'org-bullets)                                                                                                                             
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
(setq voca-builder/voca-file "~/git/lib/org/vocabulary/202104.org")
(setq voca-builder/export-file "~/.voca-builder-temp.org")
(setq voca-builder/current-tag "misc")
(setq voca-builder/current-tag "Elephant")
(setq voca-builder/current-tag "Zen")
(setq voca-builder/current-tag "Money")

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
   ))
;;
(global-set-key (kbd "C-c c") 'org-capture)
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
   "* >->-> %c :drill:\n%i")))


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