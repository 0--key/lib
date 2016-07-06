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

(require 'voca-builder)
  (setq voca-builder/voca-file "~/.vocabulary.org")
  (setq voca-builder/export-file "~/.voca-builder-temp.org")
  (setq voca-builder/current-tag "Demo")
  (global-set-key (kbd "<f4>") 'voca-builder/search-popup) 


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
   (js . t)
  ))
;; ^^^ Babel customization
(custom-set-variables
 ;; custom-set-variables was added by Custom.
 ;; If you edit it by hand, you could mess it up, so be careful.
 ;; Your init file should contain only one such instance.
 ;; If there is more than one, they won't work right.
 '(magit-diff-section-arguments (quote ("--no-ext-diff")))
 '(org-confirm-babel-evaluate nil))
;; end of custom variables
;;
;; (global-auto-revert-mode t)
;;

;; colorization
(add-to-list 'load-path "/usr/share/emacs/site-lisp/emacs-goodies-el/")
(require 'color-theme)
(eval-after-load "color-theme"
  '(progn
     (color-theme-initialize)
     (color-theme-charcoal-black)));;night)));;hober)))
(global-set-key (kbd "C-c 1") 'color-theme-charcoal-black)
(global-set-key (kbd "C-c 2") 'color-theme-digital-ofs1);; for Magit
(global-set-key (kbd "C-c 3") 'color-theme-hober)
(global-set-key (kbd "C-c 4") 'color-theme-calm-forest)
(global-set-key (kbd "C-c 5") 'color-theme-dark-gnus)
(global-set-key (kbd "C-c 6") 'color-theme-late-night)
(global-set-key (kbd "C-c 7") 'color-theme-euphoria)
(global-set-key (kbd "C-c 8") 'color-theme-retro-orange)
;;
;;
;;(require 'git)
;;(require 'git-blame)
;;
(require 'howdoi)
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
;;
;;
(setq elfeed-feeds
    '(("https://www.quora.com/Algorithms/rss" Algorithms)
      ("https://www.quora.com/Career-Advice/rss" Career)
      ("https://www.quora.com/Computer-Programmers/rss" Programmers)
      ("https://www.quora.com/Front-End-Web-Development/rss" FEWD)
      ("https://www.quora.com/Good-Habits/rss" Good-Habits)
      ("https://www.quora.com/Intelligence/rss" Intelligence)
      ("https://www.quora.com/Life/rss" Life)
      ("https://www.quora.com/Learning/rss" Learning)
      ("https://www.quora.com/Learning-to-Program/rss" Learning to Program)
      ("https://www.quora.com/Life-Advice/rss" Advice)
      ("https://www.quora.com/Linux/rss" Linux)
      ("https://www.quora.com/Mind-Tips-and-Hacks/rss" Mind Tips)
      ("https://www.quora.com/Software-Engineering/rss" Software)
      ("https://www.quora.com/Smart-People/rss" Smart People)
      ("https://www.quora.com/Sociology-of-Everyday-Life/rss" Sociology)
      ("https://www.quora.com/People-Skills/rss" Skills)
      ("https://www.quora.com/Philosophy-of-Everyday-Life/rss" Everyday)
      ("https://www.quora.com/Python-programming-language-1/rss" Python)
      ("https://www.quora.com/Web-Development/rss" Web Dev)
      ("https://www.quora.com/profile/James-Altucher/rss"  Altucher)))
(custom-set-faces
 ;; custom-set-faces was added by Custom.
 ;; If you edit it by hand, you could mess it up, so be careful.
 ;; Your init file should contain only one such instance.
 ;; If there is more than one, they won't work right.
 )
