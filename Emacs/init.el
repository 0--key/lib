(require 'package)
(add-to-list 'package-archives '("org" . "http://orgmode.org/elpa/") t)
;; and MELPA
(add-to-list 'package-archives
             '("melpa" . "https://melpa.org/packages/"))
(when (< emacs-major-version 24)
  ;; For important compatibility libraries like cl-lib
  (add-to-list 'package-archives '("gnu" . "http://elpa.gnu.org/packages/")))
;;
(package-initialize)
(elpy-enable)
 
(require 'org-bullets)
(add-hook 'org-mode-hook (lambda () (org-bullets-mode 1)))

;;
;; ######

(desktop-save-mode 1)
;;(key-chord-mode 1)
;;
(pyvenv-activate "/usr/local/share/DVCS/lib/Python/venv/")
;;(split-window-right)
;;
;; (setq default-directory "/usr/local/share/DVCS/lib/Python/edu/effectivepython/")
;; (shell "ge")
;;
;; (setq default-directory "/usr/local/share/DVCS/lib/Python/edu/python-patterns/")
;; (shell "gp")
;;
;;(setq default-directory "/usr/local/share/DVCS/lib/")
;;(shell "git")
;;(switch-to-buffer "git")
;;(buffer-menu-other-window)
;;(other-window 1)
;;
(org-babel-do-load-languages
 'org-babel-load-languages
 '((python . t)
   (emacs-lisp . t)
   (shell . t)
  ))
;; ^^^ Babel customization
(custom-set-variables
 '(org-confirm-babel-evaluate nil)
;;
 ;; ElFeed ->>
 '(elfeed-feeds
   (quote
    ("https://www.quora.com/Life/rss"
     "https://www.quora.com/Computer-Programmers/rss"
     "https://www.quora.com/Learning/rss"
     "https://www.quora.com/Python-programming-language-1/rss"
     "https://www.quora.com/Life-Advice/rss"
     "https://www.quora.com/Philosophy-of-Everyday-Life/rss"
     "https://www.quora.com/Software-Engineering/rss"
     "https://www.quora.com/Good-Habits/rss"
     "https://www.quora.com/Career-Advice/rss"
     "https://www.quora.com/Sociology-of-Everyday-Life/rss"
     "https://www.quora.com/People-Skills/rss"
     "https://www.quora.com/Linux/rss")))
 );; end of custom variables
;;
;; (global-auto-revert-mode t)
;;

;; colorization
(add-to-list 'load-path "/usr/share/emacs/site-lisp/emacs-goodies-el/")
(require 'color-theme)
(eval-after-load "color-theme"
  '(progn
     (color-theme-initialize)
     (color-theme-late-night)));;hober)))
(global-set-key (kbd "C-c 1") 'color-theme-charcoal-black)
(global-set-key (kbd "C-c 2") 'color-theme-lawrence)
(global-set-key (kbd "C-c 3") 'color-theme-lethe)
(global-set-key (kbd "C-c 4") 'color-theme-calm-forest)
(global-set-key (kbd "C-c 5") 'color-theme-dark-gnus)
(global-set-key (kbd "C-c 6") 'color-theme-late-night)
(global-set-key (kbd "C-c 7") 'color-theme-euphoria)
(global-set-key (kbd "C-c 8") 'color-theme-retro-orange)
;;
;;
(require 'git)
(require 'git-blame)
;;
(global-set-key (kbd "C-x g") 'magit-status)
(global-set-key (kbd "C-x M-g") 'magit-dispatch-popup)
;;
(setq google-translate-translation-directions-alist '(("en" . "ru")))
(setq google-translate-default-source-language "en")
(setq google-translate-default-target-language "ru")
(global-set-key (kbd "C-c t") 'google-translate-at-point)
(global-set-key (kbd "C-c T") 'google-translate-query-translate)
;;     (setq org-default-notes-file (concat org-directory "/notes.org"))
     (define-key global-map "\C-cc" 'org-capture)

 (setq org-capture-templates
       '(("t" "Todo" entry (file+headline "~/org/gtd.org" "Tasks")
	  "* TODO %?\n  %i\n  %a")
	 ("j" "Journal" entry (file+datetree "~/org/journal.org")
	  "* %?\nEntered on %U\n  %i\n  %a")))
