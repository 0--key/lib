;; ~/.emacs.d/init.el

(setq custom-file "~/.emacs.d/custom.el")
(load custom-file)
;;
(require 'package)
(add-to-list 'package-archives '("org" . "http://orgmode.org/elpa/") t)
;; and MELPA
(add-to-list 'package-archives '("melpa" . "https://melpa.org/packages/"))

(package-initialize)

(tool-bar-mode -1)
(menu-bar-mode -1)
(scroll-bar-mode -1)
(setq sentence-end-double-space nil)
(set-face-attribute 'default nil :height 130)

     (setq calendar-latitude 47.5)
     (setq calendar-longitude 34.65)
     (setq calendar-location-name "Energodar, ZP")


(elpy-enable)
(pyvenv-activate "/usr/local/share/pyVenvs/alioth/venv2Amazon/")
(pyvenv-activate "/usr/local/share/pyVenvs/alioth/venv3/")


 (require 'org-bullets)
   (add-hook 'org-mode-hook (lambda () (org-bullets-mode 1)))
;;

(add-to-list 'load-path "/usr/local/share/emacs/site-lisp/bookmark-plus/")


(require 'bookmark+)
(require 'ereader)
(require 'docker)
(require 'org-drill)
(require 'macro-commands) ;; /usr/local/git/0--key/lib/Emacs/macros.el

(require 'langtool)
(setq langtool-language-tool-jar "/usr/local/java/LanguageTool-3.6/languagetool-commandline.jar")

(global-set-key "\C-x4w" 'langtool-check)
(global-set-key "\C-x4W" 'langtool-check-done)
(global-set-key "\C-x4l" 'langtool-switch-default-language)
(global-set-key "\C-x44" 'langtool-show-message-at-point)
(global-set-key "\C-x4c" 'langtool-correct-buffer)

(setq langtool-default-language "en-US")
;;(setq langtool-java-bin "/usr/bin/java") ;; perhaps

(require 'engine-mode)
(engine-mode t)

(org-babel-do-load-languages
 'org-babel-load-languages
 '((python . t)
   (emacs-lisp . t)
   (shell . t)
   (sqlite . t)
   (sql . t)
   (octave . t)
   ))
;;

(setq org-babel-default-header-args:sh
      '((:prologue . "exec 2>&1") (:epilogue . ":"))
      )
;;
(global-set-key (kbd "C-x g") 'magit-status)
(global-set-key (kbd "C-x M-g") 'magit-dispatch-popup)

(define-key global-map "\C-cc" 'org-capture)
(global-set-key "\C-ca" 'org-agenda)
(global-set-key "\C-cl" 'org-store-link)

(key-chord-define org-mode-map "DD"     'org-drill)
(key-chord-define org-mode-map "AA"     'org-drill-again)
(key-chord-define org-mode-map "RR"     'org-drill-resume)

(key-chord-define-global "bv" 'scroll-other-window)
(key-chord-define-global "rt" 'scroll-other-window-down)

 (setq org-capture-templates
'(("p" "Todo" entry (file+headline "~/org/gtd.org" "Tasks")
   "* TODO %?\n  %i\n  %a")
  ("i" "Idiom" entry (file+headline "/usr/local/git/0--key/lib/org/drills.org" "Idioms")
   "* >->-> :drill:\n%i")
  ;;
  ("t" "Thought" entry (file+headline "/usr/local/git/0--key/lib/org/drills.org" "Thoughts")
   "* >->-> :drill:\n%i")
  ;;
  ("w" "Quote" entry (file+headline "/usr/local/git/0--key/lib/org/drills.org" "Quotes")
   "* >->-> %c :drill:\n%i")
  ;;
  ("r" "Proverb riddle" entry (file+datetree "/usr/local/git/0--key/lib/org/proverbs.org")
   "* %c\n %? %i \n %f")
  ;;
  ("o" "Proverb obvious" entry (file+datetree "/usr/local/git/0--key/lib/org/proverbs.org")
   "* %i \n %f")
  ;; 
  ("j" "Journal" entry (file+datetree "~/org/journal.org")
   "* %?\nEntered on %U\n  %i\n  %a")
;;
  ("d" "Drill-item" entry (file+headline "/usr/local/git/0--key/lib/org/drills.org" "Microservices")
   "* >->-> :drill:\n%i")))

(setq org-publish-project-alist
'(("jekyll-org"
   :base-directory "/usr/local/git/0--key/org-pub/"
   :base-extension "org"
   ;; Path to your Jekyll project.
   :publishing-directory "/usr/local/git/0--key/0--key.github.io/_posts/"
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
   :base-directory "/usr/local/git/0--key/org-pub/img/"
   :base-extension "css\\|js\\|png\\|jpg\\|gif\\|pdf\\|mp3\\|ogg\\|swf\\|php"
   :publishing-directory "/usr/local/git/0--key/0--key.io/assets/img/"
   :recursive t
   :publishing-function org-publish-attachment)

  ("jekyll" :components ("jekyll-org" "jekyll-org-img"))
  ))
;;
(require 'voca-builder)
(setq voca-builder/voca-file "/usr/local/git/0--key/lib/org/vocabulary/201904.org")
(setq voca-builder/export-file "~/.voca-builder-temp.org")
(setq voca-builder/current-tag "Harris")
(setq voca-builder/current-tag "Goleman")
(setq voca-builder/current-tag "Titans")
(setq voca-builder/current-tag "Keller")
(setq voca-builder/current-tag "eww")
