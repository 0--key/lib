;; all customization processed after init.el are there
;; it is a symlink from /usr/local/share/emacs/site-lisp/default.el
;; colorization
(require 'color-theme)
(eval-after-load "color-theme"
  '(progn
     (color-theme-initialize)
     (color-theme-ld-dark)))
     ;(color-theme-lawrence)
     ;(color-theme-euphoria)))

(global-set-key (kbd "C-c 1") 'color-theme-clarity)
(global-set-key (kbd "C-c 2") 'color-theme-ld-dark)
(global-set-key (kbd "C-c 3") 'color-theme-hober)
(global-set-key (kbd "C-c 4") 'color-theme-oswald)
(global-set-key (kbd "C-c 5") 'color-theme-tty-dark)
(global-set-key (kbd "C-c 6") 'color-theme-taming-mr-arneson)
(global-set-key (kbd "C-c 7") 'color-theme-euphoria)
(global-set-key (kbd "C-c 8") 'color-theme-lawrence)
;;
(global-set-key (kbd "C-x g") 'magit-status)
(global-set-key (kbd "C-x M-g") 'magit-dispatch-popup)
;;
(setq google-translate-translation-directions-alist '(("en" . "ru")))
(setq google-translate-default-source-language "en")
(setq google-translate-default-target-language "ru")
(global-set-key (kbd "C-c t") 'google-translate-at-point)
(global-set-key (kbd "C-c T") 'google-translate-query-translate)
;;
(global-set-key (kbd "C-c v") 'voca-builder/search-popup)
(require 'key-chord)
    (key-chord-mode 1)
    (key-chord-define-global "ws"     'smart-translate);; requres macros for n900
    (key-chord-define-global "xs"     'voca-builder/search-popup)
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

