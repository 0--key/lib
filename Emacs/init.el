(setq custom-file "~/.emacs.d/init-custom.el")
(load custom-file)
;;
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
  (setq voca-builder/voca-file "/usr/local/share/DVCS/lib/eng.org")
  (setq voca-builder/export-file "~/.voca-builder-temp.org")
  (setq voca-builder/current-tag "Quora")
;;


(require 'org-bullets)
  (add-hook 'org-mode-hook (lambda () (org-bullets-mode 1)))
;;
(desktop-save-mode 1)
(tool-bar-mode -1)
(menu-bar-mode -1)
(setq sentence-end-double-space nil)
;;
(require 'key-chord)
    (key-chord-mode 1)
    (key-chord-define-global "ww"     'google-translate-at-point)
    (key-chord-define-global "QQ"     'voca-builder/search-popup)
    (key-chord-define-global "wq"     'org-set-tags-command)
    (key-chord-define-global "]\\"     'other-frame)
;; for n900 interaction
    (key-chord-define-global "VV"     'voca-builder/search-popup)
    (key-chord-define-global "OO"     'delete-other-windows)
    (key-chord-define-global "MM"     'set-mark-command)
    (key-chord-define-global "KK"     'kill-ring-save)
    (key-chord-define-global ",,"     'org-capture)
;;
(key-chord-define org-mode-map "NN"     'org-forward-heading-same-level)
(key-chord-define org-mode-map "UU"     'org-backward-heading-same-level)
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
   (ditaa . t)
   (plantuml . t)
   ))
;;
(setq org-plantuml-jar-path
      (expand-file-name "~/.emacs.d/elpa/contrib/scripts/plantuml.jar"))
;;
;; ^^^ Babel customization
;; colorization
(add-to-list 'load-path "/usr/share/emacs/site-lisp/emacs-goodies-el/")
(require 'color-theme)
(eval-after-load "color-theme"
  '(progn
     (color-theme-initialize)
     (color-theme-ld-dark)))
(global-set-key (kbd "C-c 1") 'color-theme-charcoal-black)
(global-set-key (kbd "C-c 2") 'color-theme-ld-dark)
(global-set-key (kbd "C-c 3") 'color-theme-hober)
(global-set-key (kbd "C-c 4") 'color-theme-oswald)
(global-set-key (kbd "C-c 5") 'color-theme-tty-dark)
(global-set-key (kbd "C-c 6") 'color-theme-taming-mr-arneson)
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
'(("p" "Todo" entry (file+headline "~/org/gtd.org" "Tasks")
   "* TODO %?\n  %i\n  %a")
  ("i" "Idiom" entry (file+datetree "/usr/local/share/DVCS/lib/idioms.org")
   "* %i\n %U")
  ;;
  ("t" "Thought" entry (file+datetree "/usr/local/share/DVCS/lib/thoughts.org")
   "* %?%c\n%i\n %l")
  ;;
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
      ("https://www.quora.com/profile/James-Altucher/rss"  Altucher)
      ;; Planet Python
      ("http://planet.python.org/rss10.xml" Planet Python)
      ("http://code.activestate.com/feeds/recipes/langs/python/" Python recipes)
      ;;
      ;; ("http://feeds.feedburner.com/EnglishAsASecondLanguagePodcast" ESL)
      ;; ;; BBC podcasts there --->
      ;; ("http://downloads.bbc.co.uk/podcasts/worldservice/6min_vocab/rss.xml" 6m_voc)
      ;; ("http://downloads.bbc.co.uk/podcasts/worldservice/6min_gram/rss.xml" 6m_gram)
      ;; ("http://downloads.bbc.co.uk/podcasts/worldservice/how2/rss.xml" 6m_eng)
      ;; ("http://downloads.bbc.co.uk/podcasts/worldservice/discovery/rss.xml" Discovery)
      ;; ("http://downloads.bbc.co.uk/podcasts/worldservice/science/rss.xml" Science Hour)
      ;; ("http://www.bbc.co.uk/programmes/p00xtky9/episodes/downloads.rss" Why Factor)
      ;; ("http://www.bbc.co.uk/programmes/p02pc9zn/episodes/downloads.rss" The English We Speak)
      ;; ("http://www.bbc.co.uk/programmes/p028z2z0/episodes/downloads.rss" The Food Chain)
      ;; ("http://www.bbc.co.uk/programmes/p035w97h/episodes/downloads.rss" The Compass)
      ;; ("http://www.bbc.co.uk/programmes/b006r4vz/episodes/downloads.rss" Analysis)
      ;; ("http://www.bbc.co.uk/programmes/b006qykl/episodes/downloads.rss" In Our Time)
      ;; ("http://www.bbc.co.uk/programmes/p004kln9/episodes/downloads.rss" The Forum)
      ;; ("http://downloads.bbc.co.uk/podcasts/radio4/ta/rss.xml" Thinking Allowed)
      ))
;;
(setq org-publish-project-alist
      '(("org"
	 :base-directory "/usr/local/share/DVCS/lib/pub/"
	 :publishing-directory "/usr/local/share/DVCS/0--key.github.io"
	 :publishing-function org-html-publish-to-html
	 :section-numbers nil
	 :with-toc nil
	 )))
