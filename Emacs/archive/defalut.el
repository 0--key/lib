;; all customization processed after init.el are there
;; it is a symlink from /usr/local/share/emacs/site-lisp/default.el
;; colorization

;; (global-set-key (kbd "C-c 1") lambda (enable-theme 'tailor)) ;; not working yet
;; (global-set-key (kbd "C-c 2") (enable-theme 'desert))
;; (global-set-key (kbd "C-c 3") (enable-theme 'euphoria))
;; (global-set-key (kbd "C-c 4") (enable-theme 'dark-laptop))
;; (global-set-key (kbd "C-c 5") (enable-theme 'goldenrod))
;; (global-set-key (kbd "C-c 6") (enable-theme 'midnight))
;; (global-set-key (kbd "C-c 7") (enable-theme 'retro-green))

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
    (key-chord-define-global "bn"     'switch-to-buffers-list)
(key-chord-define-global "wx"     'simpleclip-cut)
(key-chord-define-global "wv"     'simpleclip-paste)
(key-chord-define-global "wc"     'simpleclip-copy)


;; for n900 interaction
    (key-chord-define-global "VV"     'voca-builder/search-popup)
    (key-chord-define-global "OO"     'delete-other-windows)
    (key-chord-define-global "MM"     'set-mark-command)
    (key-chord-define-global "KK"     'kill-ring-save)
    (key-chord-define-global ",,"     'org-capture)
    (key-chord-define-global "HY"     'delete-frame)
    (key-chord-define-global "ju"     'scroll-down-command)
(key-chord-define-global "hy"     'switch-to-buffer-other-frame)

;; for full-fledged keyboard
    (key-chord-define-global "'\\"     'other-frame)
;;
(key-chord-define org-mode-map "NN"     'org-forward-heading-same-level)
(key-chord-define org-mode-map "UU"     'org-backward-heading-same-level)
;;
(key-chord-define org-mode-map "''"     'org-edit-special)
(key-chord-define org-src-mode-map "''"     'org-edit-src-exit)
;;

