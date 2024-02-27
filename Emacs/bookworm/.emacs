;;
;;
(add-to-list 'package-archives
             '("melpa-stable" . "https://stable.melpa.org/packages/") t)
(package-initialize)

;; add all subdirs from the host's =site-lisp= to ~load-path~
(let* ((my-lisp-dir "/usr/local/share/emacs/site-lisp/")
       (default-directory my-lisp-dir)
       (orig-load-path load-path))
  (setq load-path (cons my-lisp-dir nil))
  (normal-top-level-add-subdirs-to-load-path)
  (nconc load-path orig-load-path))

(require 'bookmark+)
(require 'magit)
(require 'nov)
(setq nov-text-width 80)

(require 'org)
(require 'org-agenda)
(require 'org-tempo)
(require 'org-capture)
(require 'org-bullets)
(add-hook 'org-mode-hook (lambda () (org-bullets-mode 1)))
(require 'key-chord)
(key-chord-mode 1)

;; Org-capture templates in a separate file:
(load "/usr/local/share/emacs/site-lisp/custom/org-capture-templates.el")

(require 'org-drill)

(require 'google-translate)
(require 'google-translate-smooth-ui)
(setq google-translate-translation-directions-alist '(("en" . "ru")))
(setq google-translate-default-source-language "en")
(setq google-translate-default-target-language "ru")

(require 'mw-thesaurus)


(require 'python)
(require 'pyvenv)
;; (pyvenv-activate "/home/alioth/.local/venv0.1/")
;; (add-to-list 'load-path "/usr/local/share/emacs/site-lisp/elpy/")
;; (load "elpy")
;; (load "elpy-rpc")
;; (load "elpy-shell")
;; (load "elpy-profile")
;; (load "elpy-refactor")
;; (elpy-enable)

(require 'speed-type)
;; (require 'xclip)
;; (xclip-mode 1)

(load-theme 'wombat);;manoj-dark)

(require 'ivy)
(ivy-mode 1)
;; (setq ivy-use-virtual-buffers t)
;; (setq ivy-count-format "(%d/%d) ")

(require 'helpful)
(require 'which-key)
(which-key-mode)
;;======================================================
;; Additional config section:
(load "/usr/local/share/emacs/site-lisp/custom/key-chords.el")
;;
;;======================================================


;; Jekyll settings there -->
;;
(setq org-publish-project-alist
'(("jekyll-org"
   :base-directory "/home/alioth/Git/0--key/org-pub/"
   :base-extension "org"
   ;; Path to your Jekyll project.
   :publishing-directory "/home/alioth/Git/0--key/0--key.github.io/_posts/"
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
   :base-directory "/home/alioth/Git/0--key/org-pub/img/"
   :base-extension "css\\|js\\|png\\|jpg\\|gif\\|pdf\\|mp3\\|ogg\\|swf\\|php"
   :publishing-directory "/home/alioth/Git/0--key/0--key.io/assets/img/"
   :recursive t
   :publishing-function org-publish-attachment)

  ("jekyll" :components ("jekyll-org" "jekyll-org-img"))
  ))


(custom-set-variables
 ;; custom-set-variables was added by Custom.
 ;; If you edit it by hand, you could mess it up, so be careful.
 ;; Your init file should contain only one such instance.
 ;; If there is more than one, they won't work right.
 '(bmkp-last-as-first-bookmark-file "/home/alioth/.emacs.d/bookmarks")
 '(browse-url-browser-function 'eww-browse-url)
 '(org-agenda-files
   '("/home/alioth/Git/0--key/lib/org/agenda/team-tasks.list" "/home/alioth/Git/0--key/lib/org/agenda/py-genda.list" "/home/alioth/Git/0--key/lib/org/drills.org" "/home/alioth/Git/0--key/org-pub/2022-11-09-star-warmth.org" "/home/alioth/Git/0--key/org-pub/2022-11-07-cultural-differences.org" "/home/alioth/Git/0--key/org-pub/2022-01-27-cognitive-biases.org" "/home/alioth/Git/0--key/org-pub/2022-02-07-the-average-workflow.org" "/home/alioth/Git/0--key/lib/org/agenda/might-do.list"))
 '(org-agenda-scheduled-leaders '("Sch " "Sch.%2dx: "))
 '(org-agenda-window-setup 'other-window)
 '(org-babel-load-languages '((python . t) (emacs-lisp . t) (shell . t) (sqlite . t)))
 '(org-clock-auto-clockout-timer 90)
 '(org-clock-sound t)
 '(org-src-window-setup 'other-window)
 '(package-selected-packages '(sound-wav eglot xclip py-autopep8))
 '(vc-follow-symlinks t))


(custom-set-faces
 ;; custom-set-faces was added by Custom.
 ;; If you edit it by hand, you could mess it up, so be careful.
 ;; Your init file should contain only one such instance.
 ;; If there is more than one, they won't work right.
 )
