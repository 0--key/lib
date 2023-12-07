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

(require 'elpy)
(require 'speed-type)

(load-theme 'manoj-dark)

(custom-set-variables
 ;; custom-set-variables was added by Custom.
 ;; If you edit it by hand, you could mess it up, so be careful.
 ;; Your init file should contain only one such instance.
 ;; If there is more than one, they won't work right.
 '(bmkp-last-as-first-bookmark-file "/home/alioth/.emacs.d/bookmarks")
 '(package-selected-packages
   '(dictionary elpy find-file-in-project google-translate key-chord langtool nov org-bullets powerthesaurus py-autopep8 speed-type treemacs voca-builder org-drill transient dash magit popup)))
(custom-set-faces
 ;; custom-set-faces was added by Custom.
 ;; If you edit it by hand, you could mess it up, so be careful.
 ;; Your init file should contain only one such instance.
 ;; If there is more than one, they won't work right.
 )
