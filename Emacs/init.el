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

;; ######

(desktop-save-mode 1)
;;(key-chord-mode 1)
;;
(pyvenv-activate "/usr/local/share/DVCS/lib/Python/venv/")
(split-window-right)
;;
;; (setq default-directory "/usr/local/share/DVCS/lib/Python/edu/effectivepython/")
;; (shell "ge")
;;
;; (setq default-directory "/usr/local/share/DVCS/lib/Python/edu/python-patterns/")
;; (shell "gp")
;;
(setq default-directory "/usr/local/share/DVCS/lib/")
(shell "git")
;;(switch-to-buffer "git")
;;(buffer-menu-other-window)
(other-window 1)
;;
(org-babel-do-load-languages
 'org-babel-load-languages
 '((python . t)
   (emacs-lisp . t)
   (shell . t)
  ))
;; Babel customization
(custom-set-variables
 '(org-confirm-babel-evaluate nil)
 ;; ElFeed ->>
 '(elfeed-feeds
   (quote
    ("https://www.quora.com/Life/rss"
     "https://www.quora.com/Computer-Programmers/rss"
     "https://www.quora.com/Learning/rss"
     "https://www.quora.com/Python-programming-language-1/rss"
     "https://www.quora.com/Life-Advice/rss"
     "https://www.quora.com/Philosophy-of-Everyday-Life/rss"
     "https://www.quora.com/Software-Engineering/rss")))
 )
 );; end of custom variables
;;
;; (global-auto-revert-mode t)
;; colorization
(add-to-list 'load-path "/usr/share/emacs/site-lisp/emacs-goodies-el/")
(require 'color-theme)
(eval-after-load "color-theme"
  '(progn
     (color-theme-initialize)
     (color-theme-ld-dark)));;hober)))

(require 'git)
(require 'git-blame)
;;
;; (global-set-key (kbd "C-x g") 'magit-status)
;; (global-set-key (kbd "C-x M-g") 'magit-dispatch-popup)
;;
(setq google-translate-translation-directions-alist '(("en" . "ru")))
(setq google-translate-default-source-language "en")
(setq google-translate-default-target-language "ru")
(global-set-key (kbd "C-c t") 'google-translate-at-point)
(global-set-key (kbd "C-c T") 'google-translate-query-translate)
