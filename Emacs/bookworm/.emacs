(add-to-list 'package-archives
             '("melpa-stable" . "https://stable.melpa.org/packages/") t)
(package-initialize)

(require 'bookmark+)
(require 'magit)
(load-theme 'manoj-dark)

(require 'org)
(require 'org-agenda)
(require 'org-tempo)
(require 'org-bullets)
(add-hook 'org-mode-hook (lambda () (org-bullets-mode 1)))
(require 'key-chord)
(key-chord-mode 1)

;; Additional config section:
(load "/usr/local/share/emacs/site-lisp/key-chords.el")

;; Org-capture templates in a separate file:
(load "/usr/local/share/emacs/site-lisp/org-capture-templates.el")

(require 'org-drill)

(require 'google-translate)
(setq google-translate-translation-directions-alist '(("en" . "ru")))
(setq google-translate-default-source-language "en")
(setq google-translate-default-target-language "ru")

(require 'python)
(require 'pyvenv)
;;(pyvenv-activate "/home/alioth/.emacs.d/elpy/rpc-venv/") ;; restricted by elpy
;;(pyvenv-activate "/home/alioth/.local/venv0.1/")
(add-to-list 'load-path "/usr/local/share/emacs/site-lisp/elpy/")
(load "elpy")
(load "elpy-rpc")
(load "elpy-shell")
(load "elpy-profile")
(load "elpy-refactor")
;;(require 'elpy)
(elpy-enable)
(require 'speed-type)

(load-theme 'manoj-dark)

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
 '(package-selected-packages
   '(dictionary elpy find-file-in-project google-translate key-chord langtool nov org-bullets powerthesaurus py-autopep8 speed-type treemacs voca-builder org-drill transient dash magit popup)))


(custom-set-faces
 ;; custom-set-faces was added by Custom.
 ;; If you edit it by hand, you could mess it up, so be careful.
 ;; Your init file should contain only one such instance.
 ;; If there is more than one, they won't work right.
 )
