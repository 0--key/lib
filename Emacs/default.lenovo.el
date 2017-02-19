;; all customization processed after init.el are there
;; it is a symlink from /usr/local/share/emacs/site-lisp/default.el
;; colorization
(require 'color-theme)
(eval-after-load "color-theme"
  '(progn
     (color-theme-initialize)
     (color-theme-lawrence)
     (color-theme-euphoria)))

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
