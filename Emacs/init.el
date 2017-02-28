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
;;
(require 'voca-builder)
  (setq voca-builder/voca-file "/usr/local/share/DVCS/lib/org/eng.org")
  (setq voca-builder/export-file "~/.voca-builder-temp.org")
  (setq voca-builder/current-tag "Quora")
;;
(require 'bookmark+)
;;
(require 'org-bullets)
  (add-hook 'org-mode-hook (lambda () (org-bullets-mode 1)))
;;
;; (desktop-save-mode 1)
(tool-bar-mode -1)
(menu-bar-mode -1)
(scroll-bar-mode -1)
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
;; for full-fledged keyboard
    (key-chord-define-global "'\\"     'other-frame)
;;
(key-chord-define org-mode-map "NN"     'org-forward-heading-same-level)
(key-chord-define org-mode-map "UU"     'org-backward-heading-same-level)
;;
(key-chord-define org-mode-map "''"     'org-edit-special)
(key-chord-define org-src-mode-map "''"     'org-edit-src-exit)
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
   (sh . t)
   (js . t)
   (ditaa . t)
   (plantuml . t)
   (sqlite . t)
   ))
;;
(setq org-plantuml-jar-path
      (expand-file-name "~/.emacs.d/elpa/contrib/scripts/plantuml.jar"))
;;
(setq org-babel-default-header-args:sh
      '((:prologue . "exec 2>&1") (:epilogue . ":"))
      )
;;
;; ^^^ Babel customization
;;
;;(require 'git)
;;(require 'git-blame)
;;
(require 'howdoi)
;;     (setq org-default-notes-file (concat org-directory "/notes.org"))
     (define-key global-map "\C-cc" 'org-capture)

 (setq org-capture-templates
'(("p" "Todo" entry (file+headline "~/org/gtd.org" "Tasks")
   "* TODO %?\n  %i\n  %a")
  ("i" "Idiom" entry (file+datetree "/usr/local/share/DVCS/lib/org/idioms.org")
   "* %i\n %U")
  ;;
  ("t" "Thought" entry (file+datetree "/usr/local/share/DVCS/lib/org/thoughts.org")
   "* %?%c\n%i\n %l")
  ;;
    ("s" "Snippet" entry (file+headline "/usr/local/share/DVCS/lib/org/snippets.org" "init")
     "* %?\n%c\n#+BEGIN_SRC python\n%i\n#+END_SRC")
  ;;
  ("j" "Journal" entry (file+datetree "~/org/journal.org")
   "* %?\nEntered on %U\n  %i\n  %a")))
;;

;;
(setq org-publish-project-alist
'(("jekyll-org"
   :base-directory "/usr/local/share/DVCS/org-pub/"
   :base-extension "org"
   ;; Path to your Jekyll project.
   :publishing-directory "/usr/local/share/DVCS/0--key.io/_posts/"
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
   :base-directory "/usr/local/share/DVCS/org-pub/img/"
   :base-extension "css\\|js\\|png\\|jpg\\|gif\\|pdf\\|mp3\\|ogg\\|swf\\|php"
   :publishing-directory "/usr/local/share/DVCS/0--key.io/assets/img/"
   :recursive t
   :publishing-function org-publish-attachment)

  ("jekyll" :components ("jekyll-org" "jekyll-org-img"))
  ))

;;
;; http://0--key.github.io/emacs/org/export/jekyll/color-src-highlight.html
;; (setq org-html-htmlize-output-type 'css)
;; (setq org-html-htmlize-font-prefix "org-")
;;

;;
;; (require 'magit-gh-pulls)
;; (add-hook 'magit-mode-hook 'turn-on-magit-gh-pulls)
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
      ("https://www.quora.com/profile/Noam-Ben-Ami/rss" Noam)
      ("https://www.quora.com/profile/James-Altucher/rss"  Altucher)
      ("https://www.quora.com/Internship-Hiring/rss" Internship)
      ("https://www.quora.com/Hiring/rss" Hiring)
      ("https://www.quora.com/Engineering-Recruiting/rss" Recruiting)
      ("http://norvig.com/rss-feed.xml" Norvig)
      ))

