(setq custom-file "~/.emacs.d/custom_func.el")
(load custom-file)
;;
(require 'package)
(add-to-list 'package-archives '("org"
. "http://orgmode.org/elpa/") t)
;; and MELPA
(add-to-list 'package-archives '("melpa"
             . "https://melpa.org/packages/"))
(package-initialize)

(tool-bar-mode -1)
(menu-bar-mode -1)
(scroll-bar-mode -1)
(setq sentence-end-double-space nil)

(elpy-enable)
(pyvenv-activate "/usr/local/share/pyVenvs/alioth/venv2Amazon/")


 (require 'org-bullets)
   (add-hook 'org-mode-hook (lambda () (org-bullets-mode 1)))
;;

(require 'bookmark+)
(require 'ereader)
(require 'docker)
(require 'org-drill)

(require 'langtool)
(setq langtool-language-tool-jar "/usr/local/java/LanguageTool-3.6/languagetool-commandline.jar")

(global-set-key "\C-x4w" 'langtool-check)
(global-set-key "\C-x4W" 'langtool-check-done)
(global-set-key "\C-x4l" 'langtool-switch-default-language)
(global-set-key "\C-x44" 'langtool-show-message-at-point)
(global-set-key "\C-x4c" 'langtool-correct-buffer)

(setq langtool-default-language "en-US")
;;(setq langtool-java-bin "/usr/bin/java") ;; perhaps

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

 (setq org-capture-templates
'(("p" "Todo" entry (file+headline "~/org/gtd.org" "Tasks")
   "* TODO %?\n  %i\n  %a")
  ("i" "Idiom" entry (file+datetree "/usr/local/git/0--key/lib/org/idioms.org")
   "* %i\n %U")
  ;;
  ("t" "Thought" entry (file+datetree "/usr/local/git/0--key/lib/org/thoughts.org")
   "* %?%c\n%i\n %f")
  ;;
  ("r" "Proverb riddle" entry (file+datetree "/usr/local/git/0--key/lib/org/proverbs.org")
   "* %c\n %? %i \n %f")
  ;;
  ("o" "Proverb obvious" entry (file+datetree "/usr/local/git/0--key/lib/org/proverbs.org")
   "* %i \n %f")
  ;; 
  ("j" "Journal" entry (file+datetree "~/org/journal.org")
   "* %?\nEntered on %U\n  %i\n  %a")))

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
  (setq voca-builder/voca-file "/usr/local/git/0--key/lib/org/vocabulary_s_2.org")
  (setq voca-builder/export-file "~/.voca-builder-temp.org")
  (setq voca-builder/current-tag "satellite")

(custom-set-variables
 ;; custom-set-variables was added by Custom.
 ;; If you edit it by hand, you could mess it up, so be careful.
 ;; Your init file should contain only one such instance.
 ;; If there is more than one, they won't work right.
 '(Info-additional-directory-list
   (quote
    ("/usr/share/info/scrapy/" "/usr/share/info/python3.4/" "/usr/share/info/postgres/")))
 '(bmkp-last-as-first-bookmark-file "/home/alioth/.emacs.d/bookmarks")
 '(org-confirm-babel-evaluate nil)
 '(org-modules
   (quote
    (org-bbdb org-bibtex org-docview org-gnus org-info org-irc org-mhe org-rmail org-w3m org-drill)))
 '(org-src-window-setup (quote other-frame))
 '(package-selected-packages
   (quote
    (htmlize langtool org bookmark+ color-theme elfeed elpy google-translate howdoi key-chord magit marshal org-bullets org-pomodoro pcache travis voca-builder ereader docker))))
(custom-set-faces
 ;; custom-set-faces was added by Custom.
 ;; If you edit it by hand, you could mess it up, so be careful.
 ;; Your init file should contain only one such instance.
 ;; If there is more than one, they won't work right.
 )
