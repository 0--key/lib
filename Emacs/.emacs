;;
;; separate file for customization
;; version for Ubuntu Focal Fossa
;;
(setq custom-file "~/.emacs.d/custom.el")
(load custom-file)
;;
;; the single config file approach
;;
(require 'package)
(add-to-list 'package-archives '("org" . "http://orgmode.org/elpa/") t)
;; and MELPA
(add-to-list 'package-archives '("melpa" . "https://melpa.org/packages/"))

(package-initialize)

(tool-bar-mode -1)
(menu-bar-mode -1)
(scroll-bar-mode -1)
;; (desktop-save-mode 1) ;; temporary !!
(setq bmkp-propertize-bookmark-names-flag 1)
(setq sentence-end-double-space nil)
(set-face-attribute 'default nil :height 130)

     (setq calendar-latitude 47.5)
     (setq calendar-longitude 34.65)
     (setq calendar-location-name "Energodar, ZP")
;;
;;
;;
;; Purely cosmetical section
;;
(add-to-list 'custom-theme-load-path
(file-name-as-directory "/usr/local/share/emacs/site-lisp/
replace-colorthemes"))

(load-theme 'dark-laptop t t) ;; Black background is ideal for
(load-theme 'desert t t) ;; sunny day
(load-theme 'euphoria t t) ;; For  deep night work in darkness
(load-theme 'goldenrod t t)
(load-theme 'midnight t t)
(load-theme 'retro-green t t)
(load-theme 'taylor t t) ;; My fav for a fog day
(enable-theme 'desert)

 (require 'org-bullets)
   (add-hook 'org-mode-hook (lambda () (org-bullets-mode 1)))
;;
;;
;;


;;
;;
;; Utilites configuration below
(add-to-list 'load-path "/usr/local/share/emacs/site-lisp/bookmark-plus/")
(require 'bookmark+)
(require 'ereader)
;; !!(require 'docker)
(require 'org-drill)
(require 'engine-mode)
(engine-mode t)
(require 'key-chord)
(key-chord-mode 1)

(require 'voca-builder)
(setq voca-builder/voca-file "/usr/local/git/0--key/lib/org/vocabulary/202101.org")
(setq voca-builder/export-file "~/.voca-builder-temp.org")
(setq voca-builder/current-tag "Vanessa")
(setq voca-builder/current-tag "Auster")
(setq voca-builder/current-tag "Angela")
(setq voca-builder/current-tag "Greene")
(setq voca-builder/current-tag "misc")

;; !!(require 'macro-commands)
;; /usr/local/git/0--key/lib/Emacs/macros.el
;;
;;
;;

;; Programming languages for Babel

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

;;
;;
;; Natural language section below
;;
(require 'langtool)
(setq langtool-language-tool-jar
      "/usr/local/java/LanguageTool-5.0/languagetool-commandline.jar")
(setq langtool-default-language "en-US")
;;(setq langtool-java-bin "/usr/bin/java") ;; perhaps
;;
(setq google-translate-translation-directions-alist '(("en" . "ru")))
(setq google-translate-default-source-language "en")
(setq google-translate-default-target-language "ru")
;;
;;
;; This is Pytonic section
(elpy-enable)
;;(pyvenv-activate "/usr/local/share/pyVenvs/alioth/venv3/")
;;
;;
;; Plain keys for function direct access
;;
;;
;; (global-set-key "\C-x4w" 'langtool-check)
;; (global-set-key "\C-x4W" 'langtool-check-done)
;; (global-set-key "\C-x4l" 'langtool-switch-default-language)
;; (global-set-key "\C-x44" 'langtool-show-message-at-point)
;; (global-set-key "\C-x4c" 'langtool-correct-buffer)
;; (global-set-key (kbd "C-c t") 'google-translate-at-point)
;; (global-set-key (kbd "C-c T") 'google-translate-query-translate)
;; (global-set-key (kbd "C-c v") 'voca-builder/search-popup)
;;
;;
;; ^^^^^^^^^migrate out there^^^^^^^^^^^^^^^^^^^
;;
;;
(key-chord-define-global "l;"     'langtool-check)
(key-chord-define-global "l'"     'langtool-check-done)
(key-chord-define-global "lk"     'langtool-correct-buffer)
;;
(key-chord-define-global "tr"     'google-translate-at-point)
(key-chord-define-global "ty"     'voca-builder/search-popup)
;;
;;
;; KeyChords are below
;; Chords for full-fledged keyboard
(key-chord-define-global "'\\"     'other-frame)
(key-chord-define-global "';"     'other-frame)
(key-chord-define-global "bn"     'list-buffers)
(key-chord-define-global "wx"     'simpleclip-cut)
(key-chord-define-global "wv"     'simpleclip-paste)
(key-chord-define-global "wc"     'simpleclip-copy)
(key-chord-define-global "bv"     'switch-to-buffer)
(key-chord-define-global "ew"     'eval-last-sexp)
(key-chord-define-global "fd"     'previous-buffer)
(key-chord-define-global "kj"     'next-buffer)
(key-chord-define-global "q1"     'delete-other-windows)
(key-chord-define-global "w2"     'split-window-below)
(key-chord-define-global "e3"     'split-window-right)
(key-chord-define-global "sq"     'save-some-buffers)
(key-chord-define-global "fg"     'find-file)
(key-chord-define-global "bg"     'bookmark-bmenu-list)
(key-chord-define-global "sb"     'bookmark-bmenu-save)
(key-chord-define-global "ws"     'kill-ring-save)
(key-chord-define-global "wd"     'kill-region)
(key-chord-define-global "jl"     'move-end-of-line)
(key-chord-define-global "fs"     'move-beginning-of-line)
(key-chord-define-global "0o"     'delete-window)
(key-chord-define-global "bk"     'kill-buffer)
;;
;; (key-chord-define-global "ri"     'insert-register) ;; too common
(key-chord-define-global "gs"     'magit-status)
;;
(key-chord-define org-mode-map "NN"     'org-forward-heading-same-level)
(key-chord-define org-mode-map "UU"     'org-backward-heading-same-level)
;;
(key-chord-define org-mode-map "''"     'org-edit-special)
(key-chord-define org-src-mode-map "''"     'org-edit-src-exit)
;;
(key-chord-define ereader-mode-map "p;"     'google-translate-at-point)
(key-chord-define ereader-mode-map "lo"     'voca-builder/search-popup)
;;
;; for n900 interaction
;;
(key-chord-define-global "VV"     'voca-builder/search-popup)
(key-chord-define-global "OO"     'delete-other-windows)
(key-chord-define-global "MM"     'set-mark-command)
(key-chord-define-global "KK"     'kill-ring-save)
    (key-chord-define-global ",,"     'org-capture)
    (key-chord-define-global "HY"     'delete-frame)
(key-chord-define-global "ju"     'scroll-down-command)
(key-chord-define-global "hy"     'switch-to-buffer-othe-rframe)
;;
;;
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
;;
